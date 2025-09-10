from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.db.models import Cliente

PRODUTO_ID_TESTE = "1bf0f365-fbdd-4e21-9746-da27342207a9"

def test_adicionar_favorito_sucesso(client: TestClient, test_cliente: Cliente, auth_headers: dict, mock_cliente_api_produtos):
    """Testa adicionar um produto aos favoritos com sucesso."""
    mock_cliente_api_produtos.verificar_existencia_produto.return_value = True
    
    response = client.post(
        f"/api/v1/clientes/{test_cliente.id}/favoritos/",
        headers=auth_headers,
        json={"produto_id": PRODUTO_ID_TESTE}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Produto adicionado aos favoritos com sucesso."}

def test_adicionar_favorito_produto_inexistente(client: TestClient, test_cliente: Cliente, auth_headers: dict, mock_cliente_api_produtos):
    """Testa adicionar um produto que não existe na API externa."""
    mock_cliente_api_produtos.verificar_existencia_produto.return_value = False
    
    response = client.post(
        f"/api/v1/clientes/{test_cliente.id}/favoritos/",
        headers=auth_headers,
        json={"produto_id": "produto-nao-existe"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado na API externa."

def test_listar_favoritos(client: TestClient, test_cliente: Cliente, auth_headers: dict, mock_cliente_api_produtos):
    """Testa a listagem de produtos favoritos."""
    client.post(
        f"/api/v1/clientes/{test_cliente.id}/favoritos/",
        headers=auth_headers,
        json={"produto_id": PRODUTO_ID_TESTE}
    )

    mock_cliente_api_produtos.obter_detalhes_produto = AsyncMock(return_value={
        "ID": PRODUTO_ID_TESTE,
        "title": "Produto Teste",
        "brand": "Marca Teste",
        "image": "http://example.com/image.png",
        "price": 99.99,
        "reviewScore": 4.5
    })

    response = client.get(f"/api/v1/clientes/{test_cliente.id}/favoritos/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["ID"] == PRODUTO_ID_TESTE
    assert data[0]["title"] == "Produto Teste"

def test_remover_favorito(client: TestClient, test_cliente: Cliente, auth_headers: dict):
    """Testa a remoção de um produto dos favoritos."""
    client.post(
        f"/api/v1/clientes/{test_cliente.id}/favoritos/",
        headers=auth_headers,
        json={"produto_id": PRODUTO_ID_TESTE}
    )

    response = client.delete(
        f"/api/v1/clientes/{test_cliente.id}/favoritos/{PRODUTO_ID_TESTE}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response_depois = client.delete(
        f"/api/v1/clientes/{test_cliente.id}/favoritos/{PRODUTO_ID_TESTE}",
        headers=auth_headers
    )
    assert response_depois.status_code == 404
