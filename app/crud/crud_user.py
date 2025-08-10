# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.db.models import user as models
from app.schemas import user as schemas

def get_user_by_telegram_id(db: Session, telegram_id: int):
    """Busca um usuário pelo seu ID do Telegram."""
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Cria um novo usuário no banco de dados."""
    # Cria uma instância do modelo SQLAlchemy com os dados do schema
    db_user = models.User(
        telegram_id=user.telegram_id,
        first_name=user.first_name
    )
    db.add(db_user) # Adiciona à sessão
    db.commit()      # Salva no banco
    db.refresh(db_user) # Atualiza o objeto db_user com os novos dados (como o id)
    return db_user