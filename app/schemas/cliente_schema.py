import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, validator
from pydantic_core import PydanticCustomError


class ClienteDadosBasicos(BaseModel):
    email: EmailStr
    nome: str

class ClienteCadastrar(ClienteDadosBasicos):
    senha: str

    @validator('senha')
    def validar_senha(cls, v):
        if len(v) < 8:
            raise PydanticCustomError(
                'string_too_short',
                'A senha deve ter no mínimo 8 caracteres.',
                {'limit_value': 8}
            )
        if len(v) > 100:
            raise PydanticCustomError(
                'string_too_long',
                'A senha deve ter no máximo 100 caracteres.',
                {'limit_value': 100}
            )
        return v

class ClienteAtualizar(ClienteDadosBasicos):
    pass

class ClienteDetalhar(ClienteDadosBasicos):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
