# Imports de bibliotecas estándar
import logging

# Imports de terceros
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

def get_tables(db: Session):
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    
    # Log todas las tablas obtenidas
    #logging.info(f"Todas las tablas: {tables}")
    
    # Filtrar tablas específicas a excluir
    excluded_tables = {"usuarios", "activity_log","blog_posts","alembic_version"}
    
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


def get_table_data(table_name: str, db: Session, date_field: str = None, start_date: str = None, end_date: str = None):
    """
    Función para obtener todos los datos de una tabla, respetando el rango de fechas si se proporciona.
    """
    query_string = f"SELECT * FROM {table_name}"
    filters = []

    # Filtro por rango de fechas
    if date_field and start_date and end_date:
        filters.append(f"{date_field} BETWEEN '{start_date}' AND '{end_date}'")

    if filters:
        query_string += " WHERE " + " AND ".join(filters)

    result = db.execute(text(query_string))
    data = result.fetchall()
    return data