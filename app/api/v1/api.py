from fastapi import APIRouter
from app.api.v1.rotas import cliente_api, autenticacao_api, produto_favorito_api, healthcheck_api

api_router = APIRouter()
api_router.include_router(healthcheck_api.router, prefix="/healthcheck", tags=["Health Check"])
api_router.include_router(autenticacao_api.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(cliente_api.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(
    produto_favorito_api.router,
    prefix="/clientes/{id}/favoritos",
    tags=["Produtos Favoritos"]
)
