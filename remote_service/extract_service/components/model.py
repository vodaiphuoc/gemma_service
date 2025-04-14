from ._schemas import get_schema_output, ModelResult

from PIL import Image
from typing import List, Dict, Union
from types import NoneType

from gemma import gm
import numpy as np
import os
import json

from pydantic import ValidationError

SCHEMA_OUTPUT = get_schema_output()

class JAXExtractModel(object):
    r"""
    Using JAX for runing gemma3-4b-it
    """ 
    
    _prompt = f"""
- Please convert these information of candidate in CV in theses images 
into markdown text
- Your output must be structured as below format
{SCHEMA_OUTPUT}
- Here are images of the CV:
"""

    def __init__(self, max_out_length: int = 2048):
        os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"]="0.95"
        
        model = gm.nn.Gemma3_4B()
        params = gm.ckpts.load_params(gm.ckpts.CheckpointPath.GEMMA3_4B_IT)

        self._sampler = gm.text.ChatSampler(
            model = model,
            params = params,
            max_out_length = max_out_length
        )

    def forward(self,image_paths: List[str])->Dict[str, Union[bool, NoneType, ModelResult]]:
        # image pre-processing
        images_list = [np.array(Image.open(_img_path))
                  for _img_path in image_paths
                  ]

        pad_img_tokens = '\n'.join(['<start_of_image>']*len(image_paths))

        out = self._sampler.chat(
            f'{self._prompt}: \n{pad_img_tokens}',
            images = images_list,
        )

        try:
            return {
                "status": True,
                "msg": "",
                "result": ModelResult.model_validate_json(out)
            }
        
        except ValidationError as e:
            return {
                "status": False,
                "msg": e,
                "result": None
            }
        