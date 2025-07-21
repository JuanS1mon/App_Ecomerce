#!/usr/bin/env python3
"""
Script para crear manualmente las tablas de la base de datos
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_app.db.database import engine, Base
from sql_app.Services.app_stock.ot.model_ot import OT, Operacion, ReporteTiempo, OTMaterial

def create_tables():
    """Crea todas las tablas en la base de datos"""
    try:
        print("🔧 Creando tablas de la base de datos...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tablas creadas exitosamente")
        
        # Verificar que las tablas se crearon
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Tablas encontradas ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CREACIÓN DE TABLAS DE BASE DE DATOS")
    print("=" * 60)
    
    if create_tables():
        print("\n✅ ¡Tablas creadas exitosamente!")
    else:
        print("\n❌ Error al crear las tablas.")
        sys.exit(1)
