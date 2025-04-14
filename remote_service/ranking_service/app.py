
from pydantic import BaseModel
from typing import List, Dict, Union
from dotenv import load_dotenv
from loguru import logger
import uvicorn
from contextlib import asynccontextmanager
import dataclasses
import json
import itertools
import asyncio
import os


load_dotenv(dotenv_path=__file__.replace('app.py',".env")) 

from fastapi import UploadFile, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


