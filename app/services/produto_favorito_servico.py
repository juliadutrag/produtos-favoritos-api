import asyncio
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.db.models import ProdutoFavorito, Cliente
from app.schemas.produto_schema import ProdutoSchema
from app.services.api_produtos_servico import ClienteApiProdutos

async def listar_favoritos(
    db: AsyncSession,
    cliente: Cliente,
    cliente_api_produtos: ClienteApiProdutos,
) -> List[ProdutoSchema]:
    """
    Busca os IDs dos produtos favoritos do cliente no banco e os enriquece
    com os dados da API externa.
    """
    consulta = select(ProdutoFavorito.produto_id).where(ProdutoFavorito.cliente_id == cliente.id)
    resultado = await db.execute(consulta)
    ids_produtos_favoritos = resultado.scalars().all()

    if not ids_produtos_favoritos:
        return []

    tarefas_produtos = [cliente_api_produtos.obter_detalhes_produto(id_produto) for id_produto in ids_produtos_favoritos]
    resultados_produtos = await asyncio.gather(*tarefas_produtos)
    produtos_detalhados = [produto for produto in resultados_produtos if produto is not None]

    return produtos_detalhados

async def adicionar_favorito(
    db: AsyncSession,
    cliente: Cliente,
    produto_id: str,
    cliente_api_produtos: ClienteApiProdutos
) -> ProdutoFavorito:
    """
    Adiciona um novo produto à lista de favoritos de um cliente.
    """
    produto_existe = await cliente_api_produtos.verificar_existencia_produto(produto_id)
    if not produto_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado na API externa."
        )

    novo_favorito = ProdutoFavorito(cliente_id=cliente.id, produto_id=produto_id)
    db.add(novo_favorito)

    try:
        await db.commit()
        await db.refresh(novo_favorito)
        return novo_favorito
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este produto já está na lista de favoritos do cliente.",
        )

async def remover_favorito(db: AsyncSession, cliente: Cliente, produto_id: str):
    """
    Remove um produto da lista de favoritos de um cliente.
    """
    consulta = select(ProdutoFavorito).where(
        ProdutoFavorito.cliente_id == cliente.id,
        ProdutoFavorito.produto_id == produto_id
    )
    resultado = await db.execute(consulta)
    favorito_a_remover = resultado.scalars().first()

    if not favorito_a_remover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado na lista de favoritos do cliente."
        )

    await db.delete(favorito_a_remover)
    await db.commit()
