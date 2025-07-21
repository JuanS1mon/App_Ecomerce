#!/usr/bin/env python3
"""
Script para crear la tabla ot_materiales
"""

import sys
from sqlalchemy.orm import Session
from sql_app.db.database import get_db
from sqlalchemy import text

def create_ot_materiales_table():
    """Crea la tabla ot_materiales si no existe"""
    db = next(get_db())
    
    try:
        print("============================================================")
        print("🔧 CREACIÓN DE TABLA OT_MATERIALES")
        print("============================================================")
        print("🔄 Verificando si la tabla ot_materiales existe...")
        
        # Verificar si la tabla ya existe
        result = db.execute(text("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'ot_materiales'
        """))
        
        table_exists = result.fetchone()
        
        if table_exists:
            print("⚠️  La tabla 'ot_materiales' ya existe, saltando creación...")
            return True
        
        print("📝 Creando tabla ot_materiales...")
        
        # SQL para crear la tabla
        create_table_sql = """
        CREATE TABLE ot_materiales (
            id int IDENTITY(1,1) PRIMARY KEY,
            ot_id int NOT NULL,
            codigo_art int NOT NULL,
            id_deposito int NOT NULL,
            cantidad_planificada float DEFAULT 0.0,
            cantidad_utilizada float DEFAULT 0.0,
            cantidad_devuelta float DEFAULT 0.0,
            estado varchar(20) DEFAULT 'planificado',
            fecha_planificacion datetime DEFAULT GETDATE(),
            fecha_consumo datetime NULL,
            fecha_devolucion datetime NULL,
            observacion varchar(max) NULL,
            usuario_consumo varchar(100) NULL,
            nro_movimiento_stock int NULL,
            FOREIGN KEY (ot_id) REFERENCES ot(id) ON DELETE CASCADE,
            FOREIGN KEY (id_deposito) REFERENCES depositos(id)
        )
        """
        
        print("🔧 Ejecutando creación de tabla...")
        db.execute(text(create_table_sql))
        db.commit()
        print("✅ Tabla 'ot_materiales' creada exitosamente")
        
        # Crear índices para mejorar el rendimiento
        print("📝 Creando índices...")
        
        indices = [
            "CREATE INDEX ix_ot_materiales_ot_id ON ot_materiales(ot_id)",
            "CREATE INDEX ix_ot_materiales_codigo_art ON ot_materiales(codigo_art)",
            "CREATE INDEX ix_ot_materiales_estado ON ot_materiales(estado)"
        ]
        
        for index_sql in indices:
            try:
                print(f"🔧 Ejecutando: {index_sql}")
                db.execute(text(index_sql))
                db.commit()
                print("✅ Índice creado exitosamente")
            except Exception as e:
                print(f"⚠️  Error al crear índice (puede ya existir): {e}")
        
        print("✅ Tabla e índices creados exitosamente")
        
        # Verificar la estructura de la tabla creada
        print("\n🔍 Verificando estructura de la tabla creada...")
        result = db.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ot_materiales'
            ORDER BY ORDINAL_POSITION
        """))
        
        columns = result.fetchall()
        print("📋 Estructura de la tabla ot_materiales:")
        for col in columns:
            print(f"  {col[0]:<25} {col[1]:<15} {col[2]}")
        
    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = create_ot_materiales_table()
    if success:
        print("🎉 ¡Tabla ot_materiales creada exitosamente!")
    else:
        print("❌ La creación de la tabla falló.")
        sys.exit(1)
