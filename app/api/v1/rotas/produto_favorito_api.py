from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.v1.rotas.autenticacao_api import obter_cliente_autorizado
from app.db.session import get_db
from app.db.models import Cliente 
from app.schemas.produto_favorito_schema import ProdutoFavoritoAdicionar
from app.schemas.produto_schema import ProdutoSchema
from app.services import produto_favorito_servico
from app.services.api_produtos_servico import obter_cliente_api_produtos, ClienteApiProdutos

router = APIRouter()

@router.get(
    "/",
    response_model=List[ProdutoSchema],
    summary="Listar produtos favoritos de um cliente"
)
async def listar_produtos_favoritos(
    cliente_autorizado: Cliente = Depends(obter_cliente_autorizado),
    db: AsyncSession = Depends(get_db),
    cliente_api_produtos: ClienteApiProdutos = Depends(obter_cliente_api_produtos)
):
    """
    Retorna a lista de produtos favoritos de um cliente.
    """
    return await produto_favorito_servico.listar_favoritos(
        db=db, cliente=cliente_autorizado, cliente_api_produtos=cliente_api_produtos
    )

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar um produto aos favoritos do cliente logado"
)
async def adicionar_produto_favorito(
    favorito_a_adicionar: ProdutoFavoritoAdicionar,
    cliente_autorizado: Cliente = Depends(obter_cliente_autorizado),
    db: AsyncSession = Depends(get_db),
    cliente_api_produtos: ClienteApiProdutos = Depends(obter_cliente_api_produtos)
):
    """
    Adiciona um produto à lista de favoritos do cliente autenticado.
    """
    await produto_favorito_servico.adicionar_favorito(
        db=db,
        cliente=cliente_autorizado,
        produto_id=favorito_a_adicionar.produto_id,
        cliente_api_produtos=cliente_api_produtos
    )
    return {"message": "Produto adicionado aos favoritos com sucesso."}

@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover um produto dos favoritos"
)
async def remover_produto_favorito(
    produto_id: str,
    cliente_autorizado: Cliente = Depends(obter_cliente_autorizado),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove um produto da lista de favoritos do cliente autenticado.
    """
    await produto_favorito_servico.remover_favorito(
        db=db, cliente=cliente_autorizado, produto_id=produto_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
