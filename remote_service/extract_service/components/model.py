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
- Please convert these information of candidate in CV in theses images 
into markdown text
- Your output must be structured as below format
{SCHEMA_OUTPUT}
- Here are images of the CV:
"""
    def __init__(self, max_out_length:int):
        super().__init__()
        self.max_out_length = max_out_length

    @abstractmethod
    def _impl_forward(self, input_prompt:str, img_paths: List[str])->str:
        ...
    
    def forward(self,img_paths: List[str])->Dict[str, Union[bool, NoneType, ModelResult]]:
        r"""
        Main forward for all sub-classes
        """
        pad_img_tokens = '\n'.join(['<start_of_image>']*len(img_paths))
        
        _out = self._impl_forward(
            input_prompt = self._prompt + pad_img_tokens,
            img_paths = img_paths
        )
        
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
        images_list = [np.array(Image.open(_img_path))
                  for _img_path in img_paths
                  ]
        return self._sampler.chat(
            input_prompt, 
            images = images_list,
        )

        
class UnslothExtractModel(_ExtractBase):
    def __init__(self, max_out_length:int = 8000):
        super().__init__(max_out_length= max_out_length)
        from unsloth import FastLanguageModel
        from unsloth.chat_templates import get_chat_template

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = "unsloth/gemma-3-4b-pt-unsloth-bnb-4bit",
            max_seq_length = self.max_out_length,
            dtype = None,
            load_in_4bit = True,
        )
        self.model = FastLanguageModel.for_inference(model)

        self.tokenizer = get_chat_template(
            tokenizer,
            chat_template = "gemma-3"
        )

    def _impl_forward(self,input_prompt:str, img_paths: List[str])->str:
        content_parts = [{
                "type": "image",
                "image": Image.open(_img_path).convert("RGB")
            }
            for _img_path in img_paths
        ]
        content_parts.append({
            "type": "text",
            "text": input_prompt
        })
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a professtional mathematics in document understanding."}]
            },
            {
                "role": "user",
                "content": content_parts
            }
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages, 
            tokenize = True, 
            add_generation_prompt = True, 
            return_tensors = "pt"
        ).to("cuda")

        
        output_tokens =  self.model.generate(
            input_ids = inputs, 
            max_new_tokens = 
            self.max_out_length, 
            use_cache = True
        )

        print('output_tokens type: ', type(output_tokens))
        return output_tokens