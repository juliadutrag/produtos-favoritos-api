from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import uuid

from app.core import security
from app.core.config import settings
from app.db.models import Cliente
from app.db.session import get_db
from app.services import autenticacao_servico, cliente_servico

oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")
router = APIRouter()

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica o cliente e retorna um token de acesso JWT.
    """
    token = await autenticacao_servico.autenticar_cliente(
        db, email=form_data.username, password=form_data.password
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cliente = await cliente_servico.recuperar_cliente_por_email(db, email=email)
    if cliente is None:
        raise credentials_exception
    return cliente

async def obter_cliente_autorizado(
    id: uuid.UUID,
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem permissão para realizar esta ação neste recurso.",
        )
    return cliente_logado
