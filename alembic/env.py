from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Añadir la ruta del proyecto para importar modelos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from db.database import Base
    target_metadata = Base.metadata
except Exception as e:
    print(f"Warning: Could not import Base metadata: {e}")
    target_metadata = None

# Configuración Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline():
    url = os.getenv("SQLALCHEMY_DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    try:
        # Intentar obtener la URL del config
        configuration = config.get_section(config.config_ini_section, {})
        
        # Si no hay URL en config, intentar de .env
        if 'sqlalchemy.url' not in configuration:
            from dotenv import load_dotenv
            load_dotenv()
            db_url = os.getenv("SQLALCHEMY_DATABASE_URL")
            if db_url:
                configuration['sqlalchemy.url'] = db_url
        
        # Si aún no hay URL, usar un fallback
        if 'sqlalchemy.url' not in configuration:
            print("[Alembic] Advertencia: No hay sqlalchemy.url configurado")
            print("[Alembic] Las migraciones se omitirán")
            return
        
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )
            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        print(f"[Alembic] Error en run_migrations_online: {e}")
        print("[Alembic] Las migraciones se omitirán")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
