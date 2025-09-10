import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), index=True, nullable=False)
    hash_senha = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index(
            'idx_cliente_email_unico_ativo',
            email,
            unique=True,
            postgresql_where=(deleted_at.is_(None)),
            sqlite_where=(deleted_at.is_(None))
        ),
    )

class ProdutoFavorito(Base):
    __tablename__ = 'produto_favorito'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey('cliente.id', ondelete='CASCADE'), nullable=False)
    produto_id = Column(String, index=True, nullable=False)

    __table_args__ = (UniqueConstraint('cliente_id', 'produto_id', name='_cliente_produto_uc'),)
