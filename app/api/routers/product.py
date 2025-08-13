# app/api/routers/products.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.crud import crud_product
from app.schemas.product import ProductSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/", response_model=List[ProductSchema])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint da API para obter a lista de todos os produtos do catálogo.
    """
    products = crud_product.get_products(db, skip=skip, limit=limit)
    return products