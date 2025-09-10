from typing import TypeVar

from pydantic import BaseModel

T = TypeVar('T')

class RespostaPaginada[T](BaseModel):
    itens: list[T]
    total: int
    pagina: int
    tamanho: int
