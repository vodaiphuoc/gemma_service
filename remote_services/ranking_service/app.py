from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import json

from .components.agent import RankingModel
from common import (
    QueueClient, 
    make_logger,
    ExtractModelResult,
    JobDescriptions
)

ServiceLogger = make_logger("Ranking service")

from aio_pika.abc import AbstractIncomingMessage

async def message_router(
        message: AbstractIncomingMessage,
    ) -> None:
    async with message.process():
        print('message body: ', message.body)
        body = json.loads(message.body.decode())
        
        msg = body['data']
        ServiceLogger.info('app1 receive data: {msg}'.format(msg = msg))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    loop = asyncio.get_event_loop()
    model = RankingModel(api_key= os.environ['G_API_KEY'])

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


main_app = FastAPI(lifespan= lifespan, root_path="ranking_service")

@main_app.get("/")
async def index():
    return JSONResponse("hello word from ranking service")

async def main():
    config = uvicorn.Config("app:app",
                            host="0.0.0.0",
                            port=8082,
                            reload=True,
                            log_level="info"
                            )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
