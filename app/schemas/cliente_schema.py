import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ClienteDadosBasicos(BaseModel):
    email: EmailStr
    nome: str

class ClienteCadastrar(ClienteDadosBasicos):
    senha: str

class ClienteAtualizar(ClienteDadosBasicos):
    pass

class ClienteDetalhar(ClienteDadosBasicos):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
