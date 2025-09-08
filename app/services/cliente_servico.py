import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.core.security import gerar_hash_senha
from app.db.models import Cliente
from app.schemas.cliente_schema import ClienteCadastrar, ClienteAtualizar

async def criar_cliente(db: AsyncSession, cliente_cadastrar: ClienteCadastrar) -> Cliente:
    """Cria um novo cliente no banco de dados."""
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
        return cliente
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente registrado com o e-mail fornecido.",
        )

async def recuperar_cliente(db: AsyncSession, id: uuid.UUID) -> Cliente | None:
    """Busca um cliente pelo seu ID."""
    resultado = await db.execute(select(Cliente).filter(Cliente.id == id))
    return resultado.scalars().first()

async def recuperar_cliente_por_email(db: AsyncSession, email: str) -> Cliente | None:
    """Busca um cliente pelo seu email."""
    result = await db.execute(select(Cliente).filter(Cliente.email == email))
    return result.scalars().first()

async def atualizar_cliente(
    db: AsyncSession, cliente: Cliente, cliente_atualizar: ClienteAtualizar
) -> Cliente:
    """Atualiza os dados de um cliente."""
    cliente.nome = cliente_atualizar.nome
    cliente.email = cliente_atualizar.email
    await db.commit()
    await db.refresh(cliente)
    return cliente

async def excluir_cliente(db: AsyncSession, cliente: Cliente):
    """Exclui um cliente."""
    await db.delete(cliente)
    await db.commit()
