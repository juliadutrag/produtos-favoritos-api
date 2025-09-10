from fastapi.testclient import TestClient

from app.db.models import Cliente


def test_login_sucesso(client: TestClient, test_cliente: Cliente):
    """Testa o login com credenciais válidas."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "teste@exemplo.com", "password": "senha_teste"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_senha_invalida(client: TestClient, test_cliente: Cliente):
    """Testa o login com a senha incorreta."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "teste@exemplo.com", "password": "senha_errada"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha inválidos"

def test_login_email_invalido(client: TestClient):
    """Testa o login com um email que não existe."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "naoexiste@exemplo.com", "password": "senha_teste"},
    )
    assert response.status_code == 401
