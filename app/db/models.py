import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hash_senha = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class ProdutoFavorito(Base):
    __tablename__ = 'produto_favorito'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    produto_id = Column(String, index=True, nullable=False)

    __table_args__ = (UniqueConstraint('cliente_id', 'produto_id', name='_cliente_produto_uc'),)
