from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
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
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TEMPO_EXPIRACAO_TOKEN_MINUTOS)
    return jwt.encode({"sub": email, "exp": expire}, settings.CHAVE_SEGURANCA_JWT, algorithm=ALGORITHM)
