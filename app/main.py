from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.middlewares import RequestIDMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging

setup_logging()
logger = structlog.get_logger("uvicorn.access")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aplicação iniciada.", title=app.title, version=getattr(app, "version", "N/A"))
    yield
    logger.info("Aplicação encerrada.")

app = FastAPI(title=settings.TITULO_API, lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)

app.include_router(api_router, prefix="/api/v1")
