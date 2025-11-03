#!/usr/bin/env python3
"""
Script para resetear completamente Alembic
"""
import os
import sqlalchemy as sa
from sqlalchemy import text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def reset_alembic_completely():
    """Resetear completamente Alembic eliminando la tabla alembic_version"""
    
    # Variables de entorno
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Pantone123")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "tecnolarUnificado")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # URL de conexión
    database_url = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
    
    print("🧹 Reseteando completamente Alembic...")
    print(f"🔗 Conectando a: {database_url}")
    
    try:
        # Crear engine
        engine = sa.create_engine(database_url)
        
        with engine.connect() as conn:
            # Eliminar la tabla alembic_version si existe
            print("🗑️ Eliminando tabla alembic_version...")
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()
            print("✅ Tabla alembic_version eliminada")
            
    except Exception as e:
        print(f"❌ Error al resetear Alembic: {e}")
        return False
    
    print("✅ Alembic reseteado completamente")
    return True

if __name__ == "__main__":
    reset_alembic_completely()