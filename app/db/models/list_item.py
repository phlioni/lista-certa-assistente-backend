# app/db/models/list_item.py
from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base

class ListItem(Base):
    __tablename__ = "list_items"
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("shopping_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)