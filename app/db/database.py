# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Vamos criar este arquivo a seguir

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from app.db.models.user import User
from app.db.models.shopping_list import ShoppingList

# --- ADICIONE ESTA LINHA ---
from app.db.models.market import Market
from app.db.models.product import Product
from app.db.models.list_item import ListItem