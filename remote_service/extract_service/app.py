
from uuid import uuid4
from fastapi import UploadFile, Request, FastAPI, APIRouter
from fastapi.responses import JSONResponse

from typing import List, Dict, Union, Any
from types import NoneType
from loguru import logger
from contextlib import asynccontextmanager
from components import pdf2imgs, JAXExtractModel


class ModelInference(object):
    def __init__(self):
        self.engine = JAXExtractModel()
        self.pdf2imgs = pdf2imgs
    
    async def run(self, files: List[UploadFile])->List[Dict[str, Union[str, bool, NoneType, Dict[str, Any]]]]:    
        api_response_data = []

        for _file_req in files:
            _temp_file_name = f'.temp_data/temp_write_{_file_req.filename}_'+ str(uuid4())+'.pdf'
            content = await _file_req.read()
            with open(_temp_file_name, 'wb') as fp:
                fp.write(content)

            img_paths = self.pdf2imgs(_temp_file_name, resize= False)

            _results = self.engine.forward(img_paths = img_paths)
            if _results['status']:
                api_response_data.append({
                    "file_name": _file_req.filename,
                    "status": _results['status'],
                    "msg": _results['msg'],
                    "result": _results['result'].model_dump()
                })
            else:
                api_response_data.append({
                    "file_name": _file_req.filename,
                    "status": _results['status'],
                    "msg": _results['msg'],
                    "result": None
                })
        
        return api_response_data
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Setting up `ModelInference`")
    app.model = ModelInference()
    
    yield
    logger.info("Tearing Down `ModelInference`")
    app.model = None


EXTRACT_ROUTER = APIRouter(prefix= "extract", lifespan= lifespan)


@EXTRACT_ROUTER.post("/extract", response_class= JSONResponse)
async def extract(files: List[UploadFile], request: Request):
    r"""
    Receive request from local consumer
    """
    total_results = await request.app.model.run(files)
    return JSONResponse(content={
        "results":total_results 
    })