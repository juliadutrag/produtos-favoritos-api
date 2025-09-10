import uuid

import structlog
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import gerar_hash_senha
from app.db.models import Cliente
from app.schemas.cliente_schema import ClienteAtualizar, ClienteCadastrar

logger = structlog.get_logger(__name__)


async def criar_cliente(db: AsyncSession, cliente_cadastrar: ClienteCadastrar) -> Cliente:
    """Cria um novo cliente no banco de dados."""
    logger.info("Iniciando o cadastro de cliente")
    hash_senha = gerar_hash_senha(cliente_cadastrar.senha)
    cliente = Cliente(
        nome=cliente_cadastrar.nome,
        email=cliente_cadastrar.email,
        hash_senha=hash_senha
    )
    db.add(cliente)
    try:
        await db.commit()
        await db.refresh(cliente)
        logger.info(
            "Cliente cadastrado com sucesso",
            cliente_id=str(cliente.id),
        )
        return cliente
    except IntegrityError as err:
        await db.rollback()
        logger.warn("Tentativa de cadastrar cliente com e-mail já registrado previamente")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente registrado com o e-mail fornecido.",
        ) from err

async def recuperar_cliente(db: AsyncSession, id: uuid.UUID) -> Cliente | None:
    """Busca um cliente pelo seu ID."""
    logger.debug("Buscando cliente por ID", cliente_id=id)
    resultado = await db.execute(
        select(Cliente).filter(Cliente.id == id, Cliente.deleted_at.is_(None))
    )
    cliente = resultado.scalars().first()
    if cliente:
        logger.debug("Cliente encontrado por ID", cliente_id=id)
    else:
        logger.debug("Cliente não encontrado por ID", cliente_id=id)
    return cliente

async def recuperar_cliente_por_email(db: AsyncSession, email: str) -> Cliente | None:
    """Busca um cliente pelo seu email."""
    logger.debug("Buscando cliente por e-mail")
    result = await db.execute(
        select(Cliente).filter(Cliente.email == email, Cliente.deleted_at.is_(None))
    )
    cliente = result.scalars().first()

    if cliente:
        logger.debug("Cliente encontrado por e-mail")
    else:
        logger.debug("Cliente não encontrado por e-mail")

    return cliente

async def atualizar_cliente(
    db: AsyncSession, cliente: Cliente, cliente_atualizar: ClienteAtualizar
) -> Cliente:
    """Atualiza os dados de um cliente."""
    cliente_id = str(cliente.id)
    logger.info(
        "Iniciando atualização de cliente",
        cliente_id=cliente_id,
        novos_dados={"nome": cliente_atualizar.nome, "email": cliente_atualizar.email}
    )
    cliente.nome = cliente_atualizar.nome
    cliente.email = cliente_atualizar.email
    try:
        await db.commit()
        await db.refresh(cliente)
        logger.info("Cliente atualizado com sucesso", cliente_id=cliente_id)
        return cliente
    except IntegrityError as err:
        await db.rollback()
        logger.warn(
            "Tentativa de atualizar cliente para e-mail já em uso",
            cliente_id=cliente_id,
            email=cliente_atualizar.email
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O e-mail fornecido já está em uso por outro cliente.",
        ) from err
    except SQLAlchemyError as err:
        await db.rollback()
        logger.error(
            "Erro de banco de dados ao atualizar cliente",
            cliente_id=cliente_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao atualizar os dados do cliente.",
        ) from err


async def excluir_cliente(db: AsyncSession, cliente: Cliente):
    """Exclui logicamente um cliente."""
    cliente_id = str(cliente.id)
    logger.info(
        "Iniciando exclusão de cliente",
        cliente_id=cliente_id
    )

    try:
        cliente.deleted_at = func.now()
        db.add(cliente)
        await db.commit()

        logger.info(
            "Cliente excluído com sucesso",
            cliente_id=cliente_id
        )
    except SQLAlchemyError as err:
        await db.rollback()
        logger.error(
            "Erro de banco de dados ao excluir cliente",
            cliente_id=cliente_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao excluir o cliente.",
        ) from err
