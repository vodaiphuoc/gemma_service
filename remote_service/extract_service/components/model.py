from ._schemas import get_schema_output, ModelResult, EXAMPLE_CONTENTS
from .extract import read_image


from PIL import Image
from typing import List, Dict, Union, Any
from types import NoneType
from abc import ABC, abstractmethod
import numpy as np
import os
import json

from pydantic import ValidationError

SCHEMA_OUTPUT = get_schema_output()

class _ExtractBase(ABC):
    _prompt = f"""
- You are given information of the candidate in Curriculum vitae as list {{num_images}} images above.
- First, think and extract all information, here are some hints:
    - where the candidate graduated from? what is he/she major?
    - what are company the candidate has worked for? for each company, what he/she did, what to archive?
- NOTE: The information of each field (experiencs, projects, etc...) is spread across several 
above {{num_images}} images, so make sure relervant information is merged into correct field.
- Second, with intermediate results of First step, carefully parse the results into each fields of below JSON schema
for final output, dont show any else explainations.
"""
    def __init__(self, max_out_length:int):
        super().__init__()
        self.max_out_length = max_out_length

    @abstractmethod
    def _impl_forward(self, input_prompt:str, img_paths: List[str])->str:
        pass
    
    def forward(self,img_paths: List[str])->Dict[str, Union[bool, NoneType, ModelResult]]:
        r"""
        Main forward for all sub-classes
        """
        _out = self._impl_forward(
            input_prompt = self._prompt,
            img_paths = img_paths
        )

        _out = _out.replace('```json','').replace('```','')

        try:
            return {
                "status": True,
                "msg": "",
                "result": ModelResult.model_validate_json(_out)
            }
        
        except ValidationError as e:
            return {
                "status": False,
                "msg": e,
                "result": None
            }

class UnslothExtractModel(_ExtractBase):
    def __init__(self, max_out_length:int = 8000):
        super().__init__(max_out_length= max_out_length)
        from unsloth import FastLanguageModel
        from unsloth.chat_templates import get_chat_template

        self.model, preprocessor = FastLanguageModel.from_pretrained(
            # model_name = "unsloth/gemma-3-4b-pt-unsloth-bnb-4bit",
            model_name = "google/gemma-3-4b-it",
            max_seq_length = self.max_out_length,
            dtype = None,
            load_in_4bit = True,
            fast_inference = True
        )
        FastLanguageModel.for_inference(self.model)

        self.preprocessor = get_chat_template(
            preprocessor,
            chat_template = "gemma-3"
        )

    def _impl_forward(self,input_prompt:str, img_paths: List[str])->str:
        # main question
        content_parts = [{
            "type": "text",
            "text": "--- **MAIN INPUT BEGINS** ---"
        }]

        content_parts.extend([{
                "type": "image",
                "image": read_image(_img_path)
            }
            for _img_path in img_paths
        ])

        content_parts.append({
            "type": "text",
            "text": input_prompt.format(num_images = len(img_paths)) + \
                    f"\nJSON schema:\n```json\n{SCHEMA_OUTPUT}```\n" + \
                    """--- **MAIN INPUT ENDS** ---\n
**Important:** The following example is for demonstrating the desired output format only. You MUST extract 
the information from the images provided within the "MAIN INPUT BEGINS" and "MAIN INPUT ENDS" boundaries. Do not 
use any information from the example CV for the final output.
"""
        })

        # few-shot prompting
        content_parts.extend(EXAMPLE_CONTENTS)


        content_parts.append({
                'type': 'text', 
                'text': """**Now, process the CV information from the images provided at the beginning (between "MAIN INPUT BEGINS" and 
"MAIN INPUT ENDS") and output the JSON.**"""
        })

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a professtional in document understanding"}]
            },
            {
                "role": "user",
                "content": content_parts
            }
        ]

        print(messages)

        inputs = self.preprocessor.apply_chat_template(
            messages,
            add_generation_prompt = True,
            tokenize=True,
            return_dict=True,
            return_tensors = "pt"
        ).to('cuda')

        
        output_tokens =  self.model.generate(
            **inputs,
            max_new_tokens = self.max_out_length-1000,
            use_cache = True,
            temperature = 0.1
        )
        print('output_tokens shape: ', output_tokens.shape)
        return self.preprocessor.batch_decode(
            output_tokens[:, inputs['input_ids'].shape[-1]: ],
            skip_special_tokens = True
        )[0]

class JAXExtractModel(_ExtractBase):
    r"""
    Using JAX for runing gemma3-4b-it
    NOTE:
        currently OOM on colab
    """

    def __init__(self, max_out_length: int = 2048):
        super().__init__(max_out_length)
        os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"]="0.95"
        from gemma import gm

        model = gm.nn.Gemma3_4B()
        params = gm.ckpts.load_params(gm.ckpts.CheckpointPath.GEMMA3_4B_IT)

        self._sampler = gm.text.ChatSampler(
            model = model,
            params = params,
            max_out_length = self.max_out_length
        )

    def _impl_forward(self,input_prompt:str, img_paths: List[str])->str:
        pad_img_tokens = '\n'.join(['<start_of_image>']*len(img_paths))
        input_prompt += pad_img_tokens

        images_list = [np.array(Image.open(_img_path))
                  for _img_path in img_paths
                  ]
        return self._sampler.chat(
            input_prompt, 
            images = images_list,
        )
