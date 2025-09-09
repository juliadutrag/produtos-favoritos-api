from pydantic import BaseModel, HttpUrl, ConfigDict

class ProdutoSchema(BaseModel):
    ID: str
    title: str
    brand: str
    image: HttpUrl
    price: float
    reviewScore: float

    model_config = ConfigDict(from_attributes=True)
