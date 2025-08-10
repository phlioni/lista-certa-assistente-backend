# app/schemas/shopping_list.py
from pydantic import BaseModel
from datetime import datetime

# Schema base
class ShoppingListBase(BaseModel):
    name: str

# Schema para criação
class ShoppingListCreate(ShoppingListBase):
    pass

# Schema para leitura, incluindo dados do banco
class ShoppingListSchema(ShoppingListBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True