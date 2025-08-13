# app/api/deps.py
from app.db.database import SessionLocal

def get_db():
    """Cria e fornece uma sessão de base de dados para os endpoints da API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()