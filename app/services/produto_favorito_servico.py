import asyncio

import structlog
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Cliente, ProdutoFavorito
from app.schemas.produto_schema import ProdutoSchema
from app.services.api_produtos_servico import ClienteApiProdutos

logger = structlog.get_logger(__name__)


async def listar_favoritos(
    db: AsyncSession,
    cliente: Cliente,
    cliente_api_produtos: ClienteApiProdutos,
    pagina: int,
    tamanho: int
) -> tuple[list[ProdutoSchema], int]:
    """
    Busca os favoritos do cliente de forma paginada.
    """
    logger.info(
        "Iniciando listagem de produto favoritos",
        client_id=cliente.id
    )
    count = (
        select(func.count(ProdutoFavorito.produto_id))
        .where(ProdutoFavorito.cliente_id == cliente.id)
    )
    resultado_count = await db.execute(count)
    total_favoritos = resultado_count.scalar_one()

    if total_favoritos == 0:
        return [], 0

    offset = (pagina - 1) * tamanho
    consulta = (
        select(ProdutoFavorito.produto_id)
        .where(ProdutoFavorito.cliente_id == cliente.id)
        .offset(offset)
        .limit(tamanho)
    )
    resultado = await db.execute(consulta)
    ids_produtos_favoritos = resultado.scalars().all()

    if not ids_produtos_favoritos:
        return [], total_favoritos

    tarefas_produtos = [
        cliente_api_produtos.obter_detalhes_produto(id_produto) for id_produto in ids_produtos_favoritos
    ]
    resultados_produtos = await asyncio.gather(*tarefas_produtos)
    produtos_detalhados = [produto for produto in resultados_produtos if produto is not None]

    logger.info(
        "Listagem de produtos favoritos concluída",
        client_id=cliente.id,
    )
    return produtos_detalhados, total_favoritos

async def adicionar_favorito(
    db: AsyncSession,
    cliente: Cliente,
    produto_id: str,
    cliente_api_produtos: ClienteApiProdutos
) -> ProdutoFavorito:
    """
    Adiciona um novo produto à lista de favoritos de um cliente.
    """
    cliente_id_str = str(cliente.id)
    logger.info(
        "Iniciando adição de produto aos favoritos",
        client_id=cliente_id_str,
        produto_id=produto_id
    )
    produto_existe = await cliente_api_produtos.verificar_existencia_produto(produto_id)
    if not produto_existe:
        logger.warn(
            "Tentativa de adicionar produto inexistente na API externa aos favoritos",
            client_id=cliente.id,
            produto_id=produto_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado na API externa."
        )

    novo_favorito = ProdutoFavorito(cliente_id=cliente.id, produto_id=produto_id)
    db.add(novo_favorito)

    try:
        await db.commit()
        await db.refresh(novo_favorito)
        logger.info(
            "Produto adicionado aos favoritos com sucesso",
            client_id=cliente_id_str,
            produto_id=produto_id
        )
        return novo_favorito
    except IntegrityError as err:
        await db.rollback()
        logger.warn(
            "Erro ao adicionar favorito: produto já existe na lista",
            client_id=cliente_id_str,
            produto_id=produto_id
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este produto já está na lista de favoritos do cliente.",
        ) from err

async def remover_favorito(db: AsyncSession, cliente: Cliente, produto_id: str):
    """
    Remove um produto da lista de favoritos de um cliente.
    """
    logger.info(
        "Iniciando remoção de produto dos favoritos",
        client_id=cliente.id,
        produto_id=produto_id
    )
    consulta = select(ProdutoFavorito).where(
        ProdutoFavorito.cliente_id == cliente.id,
        ProdutoFavorito.produto_id == produto_id
    )
    resultado = await db.execute(consulta)
    favorito_a_remover = resultado.scalars().first()

    if not favorito_a_remover:
        logger.warn(
            "Tentativa de remover produto não encontrado nos favoritos",
            client_id=cliente.id,
            produto_id=produto_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado na lista de favoritos do cliente."
        )

    await db.delete(favorito_a_remover)
    await db.commit()
    logger.info(
        "Produto removido dos favoritos com sucesso",
        client_id=cliente.id,
        produto_id=produto_id
    )
