from uuid import uuid4
from fastapi import UploadFile, Request, FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import List, Dict, Union, Any
from types import NoneType
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import asyncio
import json

from .components import pdf2imgs, UnslothExtractModel
from common import QueueClient, make_logger
ServiceLogger = make_logger("Extract service")


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

from aio_pika.abc import AbstractIncomingMessage

async def message_decode(
        message: AbstractIncomingMessage,
        model_instance: ModelInference
    ) -> None:

    # extract data
    async with message.process():
        body = json.loads(message.body.decode())
        msg = body['data']
        ServiceLogger.info('receive data from queue: {msg}'.format(msg = msg))

        # parsing data
        


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    loop = asyncio.get_event_loop()
    model_engine = ModelInference()

    queue_client = QueueClient(
        user= os.environ['user'],
        pwd= os.environ['pwd'], 
        host_name=os.environ['hostname'], 
        port = os.environ['port'],
        queue_name = "app1",
        call_back = model_engine.run,
        service_logger="Extract service"
    )
    queue_client.start_background_task(loop)

    ServiceLogger.info('Done init')
    yield
    ServiceLogger.info('app shutting down. Cancelling background task...')
    await queue_client.stop_background_task()
    ServiceLogger.info('FastAPI app shutdown complete.')


main_app = FastAPI(lifespan= lifespan, root_path="extract_service")

@main_app.get("/")
async def index():
    return JSONResponse("hello word from extract service")

async def main():
    config = uvicorn.Config("app:app",
                            host="0.0.0.0",
                            port=8081,
                            reload=True,
                            log_level="info"
                            )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
