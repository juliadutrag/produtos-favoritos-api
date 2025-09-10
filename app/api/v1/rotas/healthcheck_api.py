from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time

from app.db.session import get_db
from app.api.v1.openapi_docs import health_check_responses

router = APIRouter()

async def checar_banco_de_dados(db: AsyncSession) -> dict:
    start_time = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        duration_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status": "ok",
            "latency_ms": round(duration_ms, 2)
        }
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status": "error",
            "detail": str(e),
            "latency_ms": round(duration_ms, 2)
        }

@router.get(
    "/",
    summary="Verifica a saúde da aplicação",
    tags=["Health Check"],
    responses=health_check_responses,
)
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica a saúde da aplicação.
    """
    bd_check = await checar_banco_de_dados(db)
    app_status = bd_check["status"]
    response_content = {
        "status": app_status,
        "checks": {
            "banco_de_dados": bd_check
        }
    }

    status_code = status.HTTP_200_OK if app_status is "ok" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(content=response_content, status_code=status_code)
