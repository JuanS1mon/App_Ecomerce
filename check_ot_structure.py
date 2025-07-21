#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla OT
"""

from sqlalchemy.orm import Session
from sql_app.db.database import get_db
from sqlalchemy import text

def check_table_structure():
    """Verifica la estructura de la tabla OT"""
    db = next(get_db())
    
    try:
        print("============================================================")
        print("🔍 VERIFICACIÓN DE ESTRUCTURA DE TABLA OT")
        print("============================================================")
        
        # Verificar si la tabla existe
        result = db.execute(text("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'ot'
        """))
        
        table_exists = result.fetchone()
        
        if not table_exists:
            print("❌ La tabla 'ot' no existe")
            return
        
        print("✅ La tabla 'ot' existe")
        print("\n📋 Columnas de la tabla OT:")
        print("-" * 60)
        
        # Obtener estructura de la tabla
        result = db.execute(text("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ot'
            ORDER BY ORDINAL_POSITION
        """))
        
        columns = result.fetchall()
        
        if not columns:
            print("❌ No se pudieron obtener las columnas de la tabla")
            return
        
        for col in columns:
            column_name, data_type, is_nullable, max_length, default = col
            length_str = f"({max_length})" if max_length else ""
            nullable_str = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_str = f"DEFAULT {default}" if default else ""
            
            print(f"  {column_name:<20} {data_type}{length_str:<15} {nullable_str:<10} {default_str}")
        
        print("\n🔍 Verificando campos esperados por el modelo:")
        print("-" * 60)
        
        expected_fields = [
            'id', 'numero', 'fecha', 'cliente', 'tipo', 'tecnico', 
            'descripcion', 'id_deposito', 'estado', 'fecha_creacion',
            'fecha_inicio', 'fecha_fin', 'id_trabajo', 'titulo', 
            'area', 'personal', 'tiempo_estimado'
        ]
        
        existing_fields = [col[0].lower() for col in columns]
        
        for field in expected_fields:
            if field.lower() in existing_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTA")
        
        print("\n📊 Registros en la tabla:")
        print("-" * 60)
        
        result = db.execute(text("SELECT COUNT(*) FROM ot"))
        count = result.fetchone()[0]
        print(f"  Total de registros: {count}")
        
        if count > 0:
            print("\n🔍 Primeros registros:")
            result = db.execute(text("SELECT TOP 5 * FROM ot"))
            records = result.fetchall()
            
            for record in records:
                print(f"  {record}")
        
    except Exception as e:
        print(f"❌ Error al verificar la estructura: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    check_table_structure()
