import os
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import USER_ROUTER

from common import (
    make_logger,
    Firebase_Client, 
    QueueProducer,
    MQ_SETTINGS,
    GENERAL_SETTINGS
)

ServiceLogger = make_logger("APP service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ServiceLogger.info('app done init')
    
    yield
    ServiceLogger.info('app shutdown complete.')


app = FastAPI(lifespan=lifespan)
app.include_router(USER_ROUTER)

async def main():
    config = uvicorn.Config("app:app",
                            host = GENERAL_SETTINGS.APPLICATION_HOST,
                            port = GENERAL_SETTINGS.APP_SERVICE_PORT,
                            reload = True,
                            log_level = "info"
                            )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
