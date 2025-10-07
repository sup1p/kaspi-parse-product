from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from src.core.config import settings
from src.models import Base


config = context.config

# Подставляем DATABASE_URL из окружения (из settings)
database_url = settings.database_url
if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

# Если DATABASE_URL использует asyncpg (для async app), то заменим драйвер на psycopg2
# чтобы Alembic использовал синхронный DBAPI и не падал с MissingGreenlet.
sync_database_url = database_url
if "+asyncpg" in database_url:
    sync_database_url = database_url.replace("+asyncpg", "+psycopg2")

# Записываем (перезаписываем) опцию в конфигурацию Alembic
config.set_main_option("sqlalchemy.url", sync_database_url)

# Настройка логирования из alembic.ini (если есть)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем metadata ваших моделей
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (sync engine)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
