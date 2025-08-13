# app/schemas/product.py
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    category: str

class ProductCreate(ProductBase):
    pass

class ProductSchema(ProductBase):
    id: int

    class Config:
        from_attributes = True