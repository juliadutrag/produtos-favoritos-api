import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.db.models import Cliente
from app.schemas.cliente_schema import ClienteCadastrar, ClienteAtualizar

async def criar_cliente(db: AsyncSession, cliente_cadastrar: ClienteCadastrar) -> Cliente:
    """Cria um novo cliente no banco de dados."""
    cliente = Cliente(nome=cliente_cadastrar.nome, email=cliente_cadastrar.email)
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

async def listar_clientes(
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> List[Cliente]:
    """
    Retorna uma lista de clientes com paginação.
    """
    query = select(Cliente).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def recuperar_cliente(db: AsyncSession, id: uuid.UUID) -> Cliente | None:
    """Busca um cliente pelo seu ID."""
    resultado = await db.execute(select(Cliente).filter(Cliente.id == id))
    return resultado.scalars().first()

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
