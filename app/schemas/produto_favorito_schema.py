from pydantic import BaseModel

class ProdutoFavoritoAdicionar(BaseModel):
    produto_id: str
