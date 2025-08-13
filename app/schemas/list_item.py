# app/schemas/list_item.py
from pydantic import BaseModel

class ListItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class ListItemCreate(ListItemBase):
    pass

class ListItemSchema(ListItemBase):
    id: int
    list_id: int

    class Config:
        from_attributes = True