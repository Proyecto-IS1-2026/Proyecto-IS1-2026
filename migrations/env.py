
from alembic import context
from sqlalchemy import create_engine, pool

from qanda.config import obtener_configuracion
from qanda.models import Base

config = context.config

target_metadata = Base.metadata

database_url = obtener_configuracion().DATABASE_URL


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name == "is1"
    return True


def run_migrations_offline():
    context.configure(
        url=database_url.render_as_string(hide_password=True),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_name=include_name,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
