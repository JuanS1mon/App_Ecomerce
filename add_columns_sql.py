#!/usr/bin/env python3
"""
Script para agregar las columnas de validación directamente con SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from sqlalchemy import text

def add_validation_columns():
    """Agregar las columnas de validación directamente"""
    db = next(get_db())

    try:
        print("Agregando columnas de validación...")

        # Agregar columna validacion_errores
        db.execute(text("""
            ALTER TABLE migraciones_metadata
            ADD validacion_errores NVARCHAR(MAX)
        """))
        print("✓ Columna 'validacion_errores' agregada")

        # Agregar columna validacion_advertencias
        db.execute(text("""
            ALTER TABLE migraciones_metadata
            ADD validacion_advertencias NVARCHAR(MAX)
        """))
        print("✓ Columna 'validacion_advertencias' agregada")

        # Agregar columna validacion_resumen
        db.execute(text("""
            ALTER TABLE migraciones_metadata
            ADD validacion_resumen NVARCHAR(MAX)
        """))
        print("✓ Columna 'validacion_resumen' agregada")

        db.commit()
        print("✓ Todas las columnas agregadas exitosamente")

    except Exception as e:
        print(f"❌ Error al agregar columnas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_validation_columns()