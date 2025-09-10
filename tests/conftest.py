import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.models import Base, Cliente, ProdutoFavorito
from app.db.session import get_db
from app.main import app
from app.core import security
from app.services.api_produtos_servico import ClienteApiProdutos, obter_cliente_api_produtos

DATABASE_URL_TESTE = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(DATABASE_URL_TESTE, echo=False, future=True)
AsyncSessionTest = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Cria as tabelas no banco de dados de teste uma vez por sessão."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine_test

@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Cria uma nova sessão de banco de dados para cada função de teste."""
    async with engine_test.begin() as connection:
        await connection.begin_nested()
        async with AsyncSessionTest(bind=connection) as session:
            await session.execute(ProdutoFavorito.__table__.delete())
            await session.execute(Cliente.__table__.delete())
            await session.commit()
            yield session
            await session.rollback()

@pytest.fixture(scope="function")
def sobrescrever_dependencias(db_session: AsyncSession, mock_cliente_api_produtos: MagicMock):
    """
    Sobrescreve as dependências da aplicação para os testes.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    def override_get_cliente_api_produtos() -> ClienteApiProdutos:
        return mock_cliente_api_produtos

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[obter_cliente_api_produtos] = override_get_cliente_api_produtos
    
    yield
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(sobrescrever_dependencias) -> TestClient:
    """Cria um TestClient para fazer requisições à API."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def mock_cliente_api_produtos() -> MagicMock:
    """Mock do serviço que consulta a API externa de produtos."""
    mock = MagicMock(spec=ClienteApiProdutos)
    mock.verificar_existencia_produto = AsyncMock(return_value=True)
    mock.obter_detalhes_produto = AsyncMock()
    return mock

@pytest_asyncio.fixture(scope="function")
async def test_cliente(db_session: AsyncSession) -> Cliente:
    """Cria um cliente no banco de dados de teste para ser usado nos endpoints."""
    cliente_data = {
        "nome": "Cliente de Teste",
        "email": "teste@exemplo.com",
        "senha": "senha_teste"
    }
    
    hash_senha = security.gerar_hash_senha(cliente_data["senha"])
    novo_cliente = Cliente(
        nome=cliente_data["nome"],
        email=cliente_data["email"],
        hash_senha=hash_senha,
        id=uuid.uuid4()
    )
    db_session.add(novo_cliente)
    await db_session.commit()
    await db_session.refresh(novo_cliente)
    return novo_cliente


@pytest.fixture(scope="function")
def auth_headers(test_cliente: Cliente) -> dict[str, str]:
    """Gera um token JWT válido e retorna o cabeçalho de autorização."""
    token = security.gerar_token(test_cliente.email)
    return {"Authorization": f"Bearer {token}"}
