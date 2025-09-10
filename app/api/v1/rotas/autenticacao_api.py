import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.db.models import Cliente
from app.db.session import get_db
from app.services import autenticacao_servico, cliente_servico

oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")
router = APIRouter()

logger = structlog.get_logger(__name__)

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica o cliente e retorna um token de acesso JWT.
    """
    username = form_data.username

    logger.info("Tentativa de login recebida", username=username)

    token = await autenticacao_servico.autenticar_cliente(
        db, email=username, password=form_data.password
    )
    if not token:
        logger.warn("Falha na autenticação", username=username, reason="Credenciais inválidas")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Login bem-sucedido", username=username)
    return {"access_token": token, "token_type": "bearer"}


async def obter_cliente_logado(
    token: str = Depends(oauth2_schema),
    db: AsyncSession = Depends(get_db)
) -> Cliente:
    """
    Decodifica o token, valida e retorna o usuário logado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais do usuário",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.CHAVE_SEGURANCA_JWT, algorithms=[security.ALGORITHM])
        id_cliente_str: str | None = payload.get("sub")

        if id_cliente_str is None:
            raise credentials_exception

        try:
            id_cliente = uuid.UUID(id_cliente_str)
        except ValueError as value_error:
            raise credentials_exception from value_error
    except JWTError as err:
        raise credentials_exception from err

    cliente = await cliente_servico.recuperar_cliente(db, id=id_cliente)
    if cliente is None:
        raise credentials_exception
    return cliente

async def obter_cliente_autorizado(
    id: uuid.UUID = Path(
        ...,
        description="ID único do cliente no formato UUID",
        example="123e4567-e89b-12d3-a456-426614174000"
    ),
    cliente_logado: Cliente = Depends(obter_cliente_logado)
) -> Cliente:
    """
    Dependência de autorização que:
    1. Garante que o usuário está autenticado (usando obter_usuario_logado).
    2. Verifica se o ID do recurso na URL é o mesmo do usuário logado.
    3. Lança uma exceção 403 Forbidden se não for o mesmo.
    4. Retorna o objeto do usuário se a verificação passar.
    """
    if id != cliente_logado.id:
        logger.warn(
            "Acesso não autorizado a recurso",
            logged_in_client_id=cliente_logado.id,
            target_resource_client_id=id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem permissão para realizar esta ação neste recurso.",
        )
    return cliente_logado
