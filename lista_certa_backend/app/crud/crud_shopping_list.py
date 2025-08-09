# app/crud/crud_shopping_list.py
from sqlalchemy.orm import Session
from app.db.models.shopping_list import ShoppingList
from app.schemas.shopping_list import ShoppingListCreate

def create_user_shopping_list(db: Session, list_data: ShoppingListCreate, user_id: int):
    """Cria uma nova lista de compras para um utilizador."""
    db_list = ShoppingList(**list_data.model_dump(), owner_id=user_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list