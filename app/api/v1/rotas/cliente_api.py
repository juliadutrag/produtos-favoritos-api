from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.rotas.autenticacao_api import obter_cliente_autorizado
from app.db.models import Cliente
from app.db.session import get_db
from app.schemas.cliente_schema import ClienteAtualizar, ClienteCadastrar, ClienteDetalhar
from app.services import cliente_servico

router = APIRouter()

@router.post(
    "/",
    response_model=ClienteDetalhar,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo cliente",
)
async def criar_cliente(
    cliente_cadastrar: ClienteCadastrar, db: AsyncSession = Depends(get_db)
) -> ClienteDetalhar:
    """
    Cria um novo cliente no sistema.
    """
    return await cliente_servico.criar_cliente(db=db, cliente_cadastrar=cliente_cadastrar)

@router.get(
    "/{id}",
    response_model=ClienteDetalhar,
    summary="Obter detalhes de um cliente",
)
async def recuperar_cliente(
    cliente: Cliente = Depends(obter_cliente_autorizado),
) -> ClienteDetalhar:
    """
    Retorna os dados de um cliente específico a partir do seu ID.
    """
    return cliente

@router.put(
    "/{id}",
    response_model=ClienteDetalhar,
    summary="Atualizar um cliente",
)
async def atualizar_cliente(
    cliente_atualizar: ClienteAtualizar,
    db: AsyncSession = Depends(get_db),
    cliente_autorizado: Cliente = Depends(obter_cliente_autorizado),
) -> ClienteDetalhar:
    """
    Atualiza os dados de um cliente existente.
    """
    return await cliente_servico.atualizar_cliente(
        db=db, cliente=cliente_autorizado, cliente_atualizar=cliente_atualizar
    )

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir um cliente",
)
async def excluir_cliente(
    db: AsyncSession = Depends(get_db),
    cliente_autorizado: Cliente = Depends(obter_cliente_autorizado),
) -> Response:
    """
    Excluir um cliente do sistema.
    """
    await cliente_servico.excluir_cliente(db=db, cliente=cliente_autorizado)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
