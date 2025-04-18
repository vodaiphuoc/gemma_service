
from uuid import uuid4
from fastapi import UploadFile, Request, FastAPI, APIRouter
from fastapi.responses import JSONResponse

import os
from typing import List, Dict, Union, Any
from types import NoneType
from loguru import logger
from contextlib import asynccontextmanager
from .components import pdf2imgs, JAXExtractModel, UnslothExtractModel

TEMP_DATA_PATH = __file__.replace("app.py",".temp_data")

class ModelInference(object):
    def __init__(self):
        self.engine = UnslothExtractModel()
        self.pdf2imgs = pdf2imgs
    
    async def run(self, files: List[UploadFile])->List[Dict[str, Union[str, bool, NoneType, Dict[str, Any]]]]:    
        api_response_data = []

        for _file_req in files:
            _temp_file_name = f'{TEMP_DATA_PATH}/temp_write_{_file_req.filename}_'+ str(uuid4())+'.pdf'
            content = await _file_req.read()
            with open(_temp_file_name, 'wb') as fp:
                fp.write(content)

            img_paths = self.pdf2imgs(_temp_file_name, resize= False)

            _results = self.engine.forward(img_paths = img_paths)
            print('_results: ', _results)

            if _results['status']:
                api_response_data.append({
                    "file_name": _file_req.filename,
                    "status": _results['status'],
                    "msg": _results['msg'],
                    "result": _results['result'].model_dump_json(indent = 2)
                })
            else:
                api_response_data.append({
                    "file_name": _file_req.filename,
                    "status": _results['status'],
                    "msg": _results['msg'],
                    "result": None
                })

            # empty temporary data
            os.remove(_temp_file_name)
            for _img_path in img_paths:
                os.remove(_img_path)
        
        return api_response_data
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Setting up `ModelInference`")
    app.model = ModelInference()
    
    yield
    logger.info("Tearing Down `ModelInference`")
    app.model = None


EXTRACT_ROUTER = APIRouter(prefix= "/extract_service", lifespan= lifespan)


@EXTRACT_ROUTER.post("/", response_class= JSONResponse)
async def extract(files: List[UploadFile], request: Request):
    r"""
    Receive request from local consumer
    """
    total_results = await request.app.model.run(files)
    return JSONResponse(content={
        "results":total_results 
    })