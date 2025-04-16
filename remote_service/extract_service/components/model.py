from ._schemas import get_schema_output, ModelResult

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
- Please understanding and convert all information of the candidate in Curriculum vitae above
- Your output must be structured as JSON with below format
{SCHEMA_OUTPUT}
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
        print('model output text: ',_out)
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
            model_name = "unsloth/gemma-3-4b-pt-unsloth-bnb-4bit",
            max_seq_length = self.max_out_length,
            dtype = None,
            load_in_4bit = True,
        )
        FastLanguageModel.for_inference(self.model)

        self.preprocessor = get_chat_template(
            preprocessor,
            chat_template = "gemma-3"
        )

        print('check type tokenizer: ', type(self.preprocessor))

    def _impl_forward(self,input_prompt:str, img_paths: List[str])->str:
        content_parts = [{
                "type": "image",
                # "image": Image.open(_img_path).convert("RGB")
            }
            for _img_path in img_paths
        ]
        content_parts.append({
            "type": "text",
            "text": input_prompt # no need to append image token here
        })
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a professtional HR reviewer of candidate CV."}]
            },
            {
                "role": "user",
                "content": content_parts
            }
        ]

        texts = self.preprocessor.apply_chat_template(
            messages,
            add_generation_prompt = True,
            # tokenize=True,
            # return_dict=True,
            # return_tensors = "pt"
        )
        
        print('text after add template: ', texts)

        inputs = self.preprocessor(
            [Image.open(_img_path).convert("RGB") for _img_path in img_paths], 
            texts,
            add_special_tokens = True,
            return_tensors = "pt",
        ).to('cuda')

        output_tokens =  self.model.generate(
            **inputs,
            max_new_tokens = self.max_out_length-2000,
            use_cache = True
        )
        print('output_tokens shape: ', output_tokens.shape)
        return self.tokenizer.batch_decode(output_tokens, skip_special_tokens = True)[0]

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
