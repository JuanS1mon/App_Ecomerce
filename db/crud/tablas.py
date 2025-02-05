import logging
from sqlalchemy.orm import Session
from sqlalchemy import inspect

def get_tables(db: Session):
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    
    # Log todas las tablas obtenidas
    #logging.info(f"Todas las tablas: {tables}")
    
    # Filtrar tablas específicas a excluir
    excluded_tables = {"usuarios", "activity_logs","blog_posts","alembic_version"}
    
    # Tablas que comienzan con "migracion_"
    tabla1 = [table for table in tables if table.startswith("migracion_") and table not in excluded_tables]
    
    # Tablas que no comienzan con "migracion_"
    tabla2 = [table for table in tables if not table.startswith("migracion_") and table not in excluded_tables]
    
    # Log las tablas filtradas
    #logging.info(f"Tablas de migraciones: {tabla1}")
    #logging.info(f"Otras tablas: {tabla2}")
    
    return tabla1, tabla2


def get_columns(table_name: str, db: Session):
    inspector = inspect(db.get_bind())
    columns = inspector.get_columns(table_name)
    column_names = [column['name'] for column in columns]
    return column_names