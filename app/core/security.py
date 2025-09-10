from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verificar_senha(senha: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash da senha."""
    return pwd_context.verify(senha, hash_senha)

def gerar_hash_senha(senha: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(senha)

def gerar_token(email: str):
    """Cria um novo token de acesso JWT."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.TEMPO_EXPIRACAO_TOKEN_MINUTOS)
    return jwt.encode({"sub": email, "exp": expire}, settings.CHAVE_SEGURANCA_JWT, algorithm=ALGORITHM)
