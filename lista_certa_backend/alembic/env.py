# alembic/env.py

import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Adiciona a pasta raiz do projeto ao path do Python
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# Importa a Base (nosso catálogo) e os modelos para registrá-los
from app.db.database import Base
from app.db import models

# Define o target_metadata a partir da Base, que agora "conhece" a tabela User
target_metadata = Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def include_object(object, name, type_, reflected, compare_to):
    """Função para dizer ao Alembic quais tabelas do PostGIS ignorar."""
    if type_ == "table" and object.schema != 'public':
        return False
    
    tables_to_ignore = [
        'spatial_ref_sys', 'topology', 'layer', 'geocode_settings',
        'direction_lookup', 'zip_lookup_base', 'zip_state',
        'zip_lookup_all', 'zip_lookup', 'secondary_unit_lookup',
        'street_type_lookup', 'state_lookup', 'place_lookup',
        'cousub_lookup', 'county_lookup', 'bg', 'addrfeat', 'addr',
        'edges', 'faces', 'featnames', 'tabblock', 'tract', 'zcta5',
        'pagc_gaz', 'pagc_lex', 'pagc_rules'
    ]
    if type_ == "table" and name in tables_to_ignore:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.environ["DATABASE_URL"]
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.environ["DATABASE_URL"]
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata, 
            include_object=include_object
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()