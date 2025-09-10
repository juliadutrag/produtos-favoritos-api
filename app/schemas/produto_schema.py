
from pydantic import BaseModel, ConfigDict, HttpUrl


class ProdutoSchema(BaseModel):
    ID: str
    title: str
    brand: str
    image: HttpUrl
    price: float
    reviewScore: float | None = None

    model_config = ConfigDict(from_attributes=True)
