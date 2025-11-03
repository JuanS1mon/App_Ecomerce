#!/usr/bin/env python3
"""
Script para agregar la columna imagen_url a la tabla ecomerce_categorias
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from db.database import SQLALCHEMY_DATABASE_URL

def add_imagen_url_column():
    """Agrega la columna imagen_url a la tabla ecomerce_categorias"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)

        with engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'ecomerce_categorias'
                AND COLUMN_NAME = 'imagen_url'
            """))

            if result.fetchone():
                print("✅ La columna imagen_url ya existe en la tabla ecomerce_categorias")
                return

            # Agregar la columna imagen_url
            print("🔄 Agregando columna imagen_url a ecomerce_categorias...")
            conn.execute(text("""
                ALTER TABLE ecomerce_categorias
                ADD imagen_url VARCHAR(500) NULL
            """))

            conn.commit()
            print("✅ Columna imagen_url agregada exitosamente")

    except Exception as e:
        print(f"❌ Error al agregar la columna: {e}")
        raise

if __name__ == "__main__":
    add_imagen_url_column()