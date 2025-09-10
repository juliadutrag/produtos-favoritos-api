import uuid
from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, validator
from pydantic_core import PydanticCustomError


class ClienteDadosBasicos(BaseModel):
    email: str
    nome: str

    @validator('email')
    def validar_email(cls, v):
        try:
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError as err:
            raise PydanticCustomError('value_error.email', 'O e-mail informado não é válido.') from err

    @validator('nome')
    def validar_nome(cls, v):
        nome_tratado = v.strip()

        if not nome_tratado:
            raise PydanticCustomError('value_error.blank', 'O nome não pode estar em branco.')

        if len(nome_tratado) < 2:
            raise PydanticCustomError(
                'string_too_short',
                'O nome deve ter no mínimo 2 caracteres.',
                {'limit_value': 2}
            )

        if len(nome_tratado) > 100:
            raise PydanticCustomError(
                'string_too_long',
                'O nome deve ter no máximo 100 caracteres.',
                {'limit_value': 100}
            )

        return nome_tratado

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
