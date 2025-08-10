# app/schemas/market.py
from pydantic import BaseModel

class MarketBase(BaseModel):
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None

class MarketCreate(MarketBase):
    pass

class MarketSchema(MarketBase):
    id: int

    class Config:
        from_attributes = True