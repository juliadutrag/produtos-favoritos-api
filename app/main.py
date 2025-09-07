from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.TITULO_API)

@app.get("/health")
def health():
    return {"status": "up"}
