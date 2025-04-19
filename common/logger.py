from loguru import logger
import sys

logger.remove()
new_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logger.add(sys.stderr, format=new_format)

def _patcher(record, prefix:str):
    record['name'] = prefix

def make_logger(prefix:str):
    r"""
    Create a custom logger for each service
    """
    return logger.patch(lambda record: _patcher(record, prefix))
