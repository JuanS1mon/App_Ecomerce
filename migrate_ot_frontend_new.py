#!/usr/bin/env python3
"""
Script para agregar las columnas de frontend a la tabla OT existente
"""

import sys
from sqlalchemy.orm import Session
from sql_app.db.database import get_db
from sqlalchemy import text

def migrate_ot_frontend():
    """Agrega las columnas necesarias para el frontend de OT"""
    db = next(get_db())
    
    try:
        print("============================================================")
        print("🔧 MIGRACIÓN DE TABLA OT PARA FRONTEND")
        print("============================================================")
        print("🔄 Iniciando migración de la tabla OT...")
        print("📝 Agregando columnas: numero, fecha, cliente, tipo, tecnico")
        
        # Lista de columnas a agregar
        columns_to_add = [
            ("numero", "VARCHAR(50) NULL"),
            ("fecha", "DATETIME NULL"),
            ("cliente", "VARCHAR(255) NULL"),
            ("tipo", "VARCHAR(50) NULL"),
            ("tecnico", "VARCHAR(100) NULL")
        ]
        
        # Verificar qué columnas ya existen
        result = db.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ot'
        """))
        
        existing_columns = [row[0].lower() for row in result.fetchall()]
        print(f"📋 Columnas existentes: {existing_columns}")
        
        # Agregar cada columna si no existe
        for column_name, column_definition in columns_to_add:
            if column_name.lower() not in existing_columns:
                try:
                    sql = f"ALTER TABLE ot ADD {column_name} {column_definition}"
                    print(f"🔧 Ejecutando: {sql}")
                    db.execute(text(sql))
                    db.commit()
                    print(f"✅ Columna '{column_name}' agregada exitosamente")
                except Exception as e:
                    print(f"❌ Error al agregar columna '{column_name}': {e}")
                    db.rollback()
            else:
                print(f"⚠️  Columna '{column_name}' ya existe, saltando...")
        
        print("✅ Migración completada exitosamente")
        
        # Verificar las columnas después de la migración
        print("\n🔍 Verificando estructura final...")
        result = db.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ot'
            ORDER BY ORDINAL_POSITION
        """))
        
        final_columns = result.fetchall()
        print("📋 Estructura final de la tabla OT:")
        for col in final_columns:
            print(f"  {col[0]:<20} {col[1]:<15} {col[2]}")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = migrate_ot_frontend()
    if success:
        print("🎉 ¡Migración completada exitosamente!")
    else:
        print("❌ La migración falló.")
        sys.exit(1)
