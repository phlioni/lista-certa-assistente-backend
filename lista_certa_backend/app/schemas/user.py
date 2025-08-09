# app/schemas/user.py
from pydantic import BaseModel
from datetime import datetime

# Schema base com os campos comuns
class UserBase(BaseModel):
    telegram_id: int
    first_name: str | None = None # O nome pode ser opcional

# Schema para a criação de um usuário (o que recebemos de entrada)
class UserCreate(UserBase):
    pass

# Schema completo para leitura (o que retornamos do banco)
# Inclui os campos que o banco gera (id, created_at)
class UserSchema(UserBase):
    id: int
    is_premium: bool
    created_at: datetime

    class Config:
        # Esta linha mágica permite que o Pydantic leia
        # os dados diretamente de um objeto do SQLAlchemy
        from_attributes = True