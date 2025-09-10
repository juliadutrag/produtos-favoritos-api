from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import gerar_token, verificar_senha
from app.db.models import Cliente
from app.services import cliente_servico


async def autenticar_cliente(db: AsyncSession, email: str, password: str) -> Cliente | None:
    """
    Autentica um usuário (neste caso, um cliente).
    Retorna o objeto do cliente se as credenciais forem válidas, senão None.
    """
    cliente = await cliente_servico.recuperar_cliente_por_email(db, email=email)

    if not cliente or not verificar_senha(password, cliente.hash_senha):
        return None

    return gerar_token(cliente.email)
