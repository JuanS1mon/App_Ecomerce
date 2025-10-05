#!/usr/bin/env python3
"""
Script para inspeccionar completamente la tabla alembic_version
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_TYPE = os.getenv("DB_TYPE", "sqlserver").split('#')[0].strip()
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "sqlapp")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

if DB_TYPE == "sqlserver":
    SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def inspect_alembic_version():
    """Inspeccionar completamente la tabla alembic_version"""
    try:
        with engine.connect() as connection:
            # Verificar si existe la tabla
            result = connection.execute(text("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'alembic_version'
            """))
            
            if not result.fetchone():
                print("❌ La tabla alembic_version no existe")
                return
            
            print("✅ La tabla alembic_version existe")
            
            # Obtener la estructura de la tabla
            result = connection.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'alembic_version'
                ORDER BY ORDINAL_POSITION
            """))
            
            print("\n📋 Estructura de la tabla:")
            for row in result.fetchall():
                print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
            
            # Obtener todos los datos
            result = connection.execute(text("SELECT * FROM alembic_version"))
            rows = result.fetchall()
            
            print(f"\n📊 Contenido de la tabla ({len(rows)} filas):")
            for i, row in enumerate(rows):
                print(f"  Fila {i+1}: {row}")
            
            if not rows:
                print("  (tabla vacía)")
            
            return rows
            
    except Exception as e:
        print(f"❌ Error al inspeccionar alembic_version: {e}")
        return None

def fix_alembic_by_force():
    """Forzar una corrección de alembic_version"""
    try:
        with engine.connect() as connection:
            # Eliminar cualquier contenido existente
            connection.execute(text("DELETE FROM alembic_version"))
            connection.commit()
            print("✅ Tabla alembic_version limpiada")
            
            # Insertar la versión correcta
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('163506fcdd36')"))
            connection.commit()
            print("✅ Versión 163506fcdd36 insertada")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al forzar corrección: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Inspeccionando tabla alembic_version...")
    print(f"🔗 Conectando a: {SQLALCHEMY_DATABASE_URL}")
    
    rows = inspect_alembic_version()
    
    if rows is not None:
        print("\n🔧 ¿Intentar forzar corrección? (esto limpiará y establecerá la versión correcta)")
        # Automaticamente forzar la corrección
        success = fix_alembic_by_force()
        
        if success:
            print("\n✅ Corrección forzada completada")
            print("Verifica de nuevo:")
            inspect_alembic_version()
        else:
            print("\n❌ No se pudo forzar la corrección")