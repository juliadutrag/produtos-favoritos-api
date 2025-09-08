import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class ClienteDadosBasicos(BaseModel):
    email: EmailStr
    nome: str

class ClienteCadastrar(ClienteDadosBasicos):
    pass

class ClienteAtualizar(ClienteDadosBasicos):
    pass

class ClienteDetalhar(ClienteDadosBasicos):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
