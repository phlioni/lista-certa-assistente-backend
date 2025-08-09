# app/crud/crud_market.py
from sqlalchemy.orm import Session
from app.db.models.market import Market
from app.schemas.market import MarketCreate

def create_market(db: Session, market: MarketCreate):
    """Cria um novo mercado no banco de dados."""
    db_market = Market(**market.model_dump())
    db.add(db_market)
    db.commit()
    db.refresh(db_market)
    return db_market