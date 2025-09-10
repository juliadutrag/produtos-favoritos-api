from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import produto_favorito_servico


@pytest.mark.asyncio
async def test_listar_favoritos_com_sucesso():
    """
    Testa o cenário feliz de listar favoritos, mocando o DB e a API externa.
    """
    mock_cliente = MagicMock()
    mock_cliente.id = "id_cliente_teste"

    mock_db = AsyncMock()
    ids_produtos_favoritos = ["id_produto_1", "id_produto_2"]
    total_de_favoritos = 2

    mock_resultado_count = MagicMock()
    mock_resultado_count.scalar_one.return_value = total_de_favoritos

    mock_resultado_select = MagicMock()
    mock_resultado_select.scalars.return_value.all.return_value = ids_produtos_favoritos

    mock_db.execute.side_effect = [mock_resultado_count, mock_resultado_select]

    mock_api_produtos = AsyncMock()
    produto_detalhado_1 = {"ID": "id_produto_1", "title": "Produto 1"}
    produto_detalhado_2 = {"ID": "id_produto_2", "title": "Produto 2"}

    mock_api_produtos.obter_detalhes_produto.side_effect = [
        produto_detalhado_1,
        produto_detalhado_2,
    ]

    produtos, total = await produto_favorito_servico.listar_favoritos(
        db=mock_db,
        cliente=mock_cliente,
        cliente_api_produtos=mock_api_produtos,
        pagina=1,
        tamanho=10
    )

    assert total == total_de_favoritos
    assert len(produtos) == 2
    assert produtos[0]["title"] == "Produto 1"
    assert produtos[1]["title"] == "Produto 2"

    assert mock_api_produtos.obter_detalhes_produto.call_count == 2
    mock_api_produtos.obter_detalhes_produto.assert_any_call("id_produto_1")
    mock_api_produtos.obter_detalhes_produto.assert_any_call("id_produto_2")


@pytest.mark.asyncio
async def test_listar_favoritos_quando_cliente_nao_tem_favoritos():
    """
    Testa o cenário em que o cliente não possui produtos favoritos.
    """
    mock_cliente = MagicMock()
    mock_cliente.id = "id_cliente_teste"
    mock_db = AsyncMock()
    mock_api_produtos = AsyncMock()

    mock_resultado_count = MagicMock()
    mock_resultado_count.scalar_one.return_value = 0
    mock_db.execute.return_value = mock_resultado_count

    produtos, total = await produto_favorito_servico.listar_favoritos(
        db=mock_db,
        cliente=mock_cliente,
        cliente_api_produtos=mock_api_produtos,
        tamanho=10,
        pagina=1
    )

    assert produtos == []
    assert total == 0

    mock_api_produtos.obter_detalhes_produto.assert_not_called()


@pytest.mark.asyncio
async def test_listar_favoritos_quando_api_externa_falha_para_um_produto():
    """
    Testa o cenário onde a API externa não encontra um dos produtos favoritados.
    """
    mock_cliente = MagicMock()
    mock_cliente.id = "id_cliente_teste"
    mock_db = AsyncMock()
    ids_produtos_favoritos = ["id_produto_1", "id_produto_nao_encontrado"]

    mock_resultado_count = MagicMock()
    mock_resultado_count.scalar_one.return_value = 2

    mock_resultado_select = MagicMock()
    mock_resultado_select.scalars.return_value.all.return_value = ids_produtos_favoritos

    mock_db.execute.side_effect = [mock_resultado_count, mock_resultado_select]

    mock_api_produtos = AsyncMock()
    produto_detalhado_1 = {"ID": "id_produto_1", "title": "Produto 1"}

    mock_api_produtos.obter_detalhes_produto.side_effect = [
        produto_detalhado_1,
        None,
    ]

    produtos, total = await produto_favorito_servico.listar_favoritos(
        db=mock_db,
        cliente=mock_cliente,
        cliente_api_produtos=mock_api_produtos,
        pagina=1,
        tamanho=10
    )

    assert total == 2
    assert len(produtos) == 1
    assert produtos[0]["title"] == "Produto 1"
    assert mock_api_produtos.obter_detalhes_produto.call_count == 2
