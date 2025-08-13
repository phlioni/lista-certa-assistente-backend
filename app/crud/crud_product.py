# app/crud/crud_product.py
from sqlalchemy.orm import Session
from app.db.models.product import Product
from app.schemas.product import ProductCreate

def create_product(db: Session, product: ProductCreate):
    """Cria um novo produto no catálogo."""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Busca todos os produtos do catálogo."""
    return db.query(Product).offset(skip).limit(limit).all()

def get_product_by_name(db: Session, name: str):
    """Busca um produto pelo nome."""
    return db.query(Product).filter(Product.name == name).first()