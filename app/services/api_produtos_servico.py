import time
from typing import Any

import httpx
import structlog
from fastapi import HTTPException, status

from app.core.config import settings

logger = structlog.get_logger(__name__)

class ClienteApiProdutos:
    """
    Cliente para interagir com a API externa de produtos.
    """
    def __init__(self):
        self.url_base = f"{settings.URL_BASE_API_PRODUTO}/products"

    async def obter_detalhes_produto(self, id_produto: str) -> dict[str, Any] | None:
        """
        Busca os detalhes de um produto específico na API externa.
        Retorna um dicionário com os dados do produto ou None se não for encontrado.
        """
        url = f"{self.url_base}/{id_produto}/"
        async with httpx.AsyncClient() as client:
            try:
                start_time = time.monotonic()
                logger.debug("Chamando API externa de produtos", url=url)

                resposta = await client.get(url, timeout=10.0)
                duracao = (time.monotonic() - start_time) * 1000
                logger.info(
                    "Resposta recebida da API externa de produtos",
                    url=url,
                    status_code=resposta.status_code,
                    duration_ms=round(duracao, 2)
                )
                if resposta.status_code == 200:
                    return resposta.json()
                elif resposta.status_code == 404:
                    return None
                else:
                    resposta.raise_for_status()

            except httpx.RequestError as exc:
                logger.error("Erro de comunicação com a API de produtos", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="O serviço externo de produtos está indisponível."
                ) from exc
        return None

    async def verificar_existencia_produto(self, id_produto: str) -> bool:
        """
        Verifica de forma rápida se um produto existe na API externa.
        """
        detalhes = await self.obter_detalhes_produto(id_produto)
        return detalhes is not None

def obter_cliente_api_produtos() -> ClienteApiProdutos:
    """
    Dependência do FastAPI que cria e retorna uma instância do cliente da API de produtos.
    """
    return ClienteApiProdutos()
