# app/db/models/__init__.py

from app.db.database import Base
from .user import User

# No futuro, quando você criar mais tabelas (ex: Market, List),
# você também precisará importá-las aqui para que o Alembic as encontre.