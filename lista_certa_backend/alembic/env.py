# alembic/env.py

import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adiciona o caminho do projeto ao path do python para encontrar os módulos
# Isso é crucial para que o Alembic "enxergue" seus modelos do SQLAlchemy
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()  # Carrega as variáveis do arquivo .env

# Importa a Base dos seus modelos
from app.db import models
# Importa todos os modelos para que o autogenerate os detecte
from app.db.database import Base
from app.db import models # Importa o "índice" de modelos

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # CORREÇÃO: Usar .metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.environ["DATABASE_URL"] # Lê a URL do ambiente
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Pega a configuração da seção [alembic] do alembic.ini
    configuration = config.get_section(config.config_ini_section)
    # **AQUI ESTÁ A MÁGICA**: Injeta a URL do banco de dados lida do .env
    configuration["sqlalchemy.url"] = os.environ["DATABASE_URL"]

    # alembic/env.py -> dentro da função run_migrations_online

    def include_object(object, name, type_, reflected, compare_to):
       
        # Lista exaustiva de tabelas a serem ignoradas
            tables_to_ignore = [
                'spatial_ref_sys', 'topology', 'layer', 'geocode_settings',
                'direction_lookup', 'zip_lookup_base', 'zip_state',
                'zip_lookup_all', 'zip_lookup', 'secondary_unit_lookup',
                'street_type_lookup', 'state_lookup', 'place_lookup',
                'cousub_lookup', 'county_lookup', 'bg', 'addrfeat', 'addr',
                'edges', 'faces', 'featnames', 'tabblock', 'tract', 'zcta5',
                'pagc_gaz', 'pagc_lex', 'pagc_rules'
            ]

            # Ignora qualquer tabela que não esteja no schema 'public' (principal)
            if type_ == "table" and object.schema != 'public':
                return False
            
            # Ignora as tabelas da lista se estiverem no schema 'public'
            if type_ == "table" and name in tables_to_ignore:
                return False

            return True
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()