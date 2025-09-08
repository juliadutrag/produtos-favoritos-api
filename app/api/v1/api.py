from fastapi import APIRouter
from app.api.v1.rotas import cliente_api

api_router = APIRouter()
api_router.include_router(cliente_api.router, prefix="/clientes", tags=["clientes"])
