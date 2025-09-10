import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Cliente


def test_criar_cliente_sucesso(client: TestClient):
    """Testa a criação de um novo cliente."""
    response = client.post(
        "/api/v1/clientes/",
        json={"nome": "Novo Cliente", "email": "novo@exemplo.com", "senha": "123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "novo@exemplo.com"
    assert "id" in data

def test_criar_cliente_email_duplicado(client: TestClient, test_cliente: Cliente):
    """Testa criar um cliente com um e-mail que já existe."""
    response = client.post(
        "/api/v1/clientes/",
        json={"nome": "Outro Nome", "email": test_cliente.email, "senha": "123"}
    )
    assert response.status_code == 409

def test_recuperar_cliente_autorizado(client: TestClient, test_cliente: Cliente, auth_headers: dict):
    """Testa recuperar os próprios dados quando autenticado."""
    response = client.get(f"/api/v1/clientes/{test_cliente.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(test_cliente.id)

def test_recuperar_cliente_nao_autorizado(client: TestClient, test_cliente: Cliente):
    """Testa falha ao tentar recuperar dados sem autenticação."""
    response = client.get(f"/api/v1/clientes/{test_cliente.id}")
    assert response.status_code == 401

def test_atualizar_cliente_sucesso(client: TestClient, test_cliente: Cliente, auth_headers: dict):
    """Testa a atualização bem-sucedida dos próprios dados."""
    response = client.put(
        f"/api/v1/clientes/{test_cliente.id}",
        headers=auth_headers,
        json={"nome": "Nome Atualizado", "email": "email.atualizado@exemplo.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Nome Atualizado"
    assert data["email"] == "email.atualizado@exemplo.com"

@pytest.mark.asyncio
async def test_excluir_cliente_sucesso(
    client: TestClient,
    test_cliente: Cliente,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Testa a exclusão bem-sucedida da própria conta."""
    response = client.delete(f"/api/v1/clientes/{test_cliente.id}", headers=auth_headers)
    assert response.status_code == 204

    await db_session.refresh(test_cliente)
    assert test_cliente.deleted_at is not None

    response_depois = client.get(f"/api/v1/clientes/{test_cliente.id}", headers=auth_headers)
    assert response_depois.status_code == 401
