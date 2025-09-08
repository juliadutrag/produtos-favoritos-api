from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(title=settings.TITULO_API)

@app.get("/health")
def health():
    return {"status": "up"}

app.include_router(api_router, prefix="/api/v1")
