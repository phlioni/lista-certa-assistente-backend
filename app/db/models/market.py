# app/db/models/market.py
from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, nullable=True) # Endereço completo
    latitude = Column(Float, nullable=True)  # Para geolocalização
    longitude = Column(Float, nullable=True) # Para geolocalização