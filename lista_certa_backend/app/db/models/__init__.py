# app/db/models/__init__.py

from app.db.database import Base
from .user import User

# No futuro, quando você criar mais modelos (ex: Listas, Mercados),
# você vai importá-los aqui também.