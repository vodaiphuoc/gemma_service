from loguru import logger
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .components.agent import RankingModel
from common.schemas import ExtractModelResult, JobDescriptions

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Setting up `RankingModel`")
    app.model = RankingModel(api_key= os.environ['G_API_KEY'])
    
    yield
    logger.info("Tearing Down `RankingModel`")
    app.model = None

RANKING_ROUTER = APIRouter(prefix= "/ranking_service", lifespan= lifespan)

@RANKING_ROUTER.post("/", response_class= JSONResponse)
async def ranking(
    extracted_results: ExtractModelResult, 
    jd: JobDescriptions,
    secret_bias: str, 
    request: Request
    ):
    r"""
    Receive request from local consumer
    """
    return JSONResponse(content={
        "results":request.app.model.forward(
            extracted_results = extracted_results, 
            jd = jd,
            secret_bias = secret_bias
        ) 
    })