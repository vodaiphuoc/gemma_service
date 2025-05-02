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
    JobDescriptions,
    MQ_SETTINGS,
    GENERAL_SETTINGS
)

ServiceLogger = make_logger("Ranking service")

from aio_pika.abc import AbstractIncomingMessage

async def message_handler(
        message: AbstractIncomingMessage,
        model: RankingModel
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
        user = MQ_SETTINGS.USER, 
        pwd = MQ_SETTINGS.PWD, 
        host_name = MQ_SETTINGS.HOSTNAME, 
        port = MQ_SETTINGS.PORT,
        queue_name = MQ_SETTINGS.RANKING_SERVICE_QUEUE_NAME,
        call_back = message_handler,
        service_logger = ServiceLogger,
        model = model
    )
    queue_client.start_background_task(loop)

    ServiceLogger.info('app done init')
    yield
    ServiceLogger.info('app shutting down. Cancelling background task...')
    await queue_client.stop_background_task()
    ServiceLogger.info('app shutdown complete.')


main_app = FastAPI(lifespan= lifespan, root_path="ranking_service")

@main_app.get("/")
async def index():
    return JSONResponse("hello word from ranking service")

async def main():
    config = uvicorn.Config("app:app",
                            host = GENERAL_SETTINGS.APPLICATION_HOST,
                            port = GENERAL_SETTINGS.RANKING_SERVICE_PORT,
                            reload=True,
                            log_level="info"
                            )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
