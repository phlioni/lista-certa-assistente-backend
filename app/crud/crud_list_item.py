# app/crud/crud_list_item.py
from sqlalchemy.orm import Session
from app.db.models.list_item import ListItem
from app.schemas.list_item import ListItemCreate

def add_item_to_list(db: Session, item: ListItemCreate, list_id: int):
    """Adiciona um item a uma lista de compras específica."""
    db_item = ListItem(
        product_id=item.product_id,
        quantity=item.quantity,
        list_id=list_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item