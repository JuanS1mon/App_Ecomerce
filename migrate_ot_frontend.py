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
        cursor.execute("SELECT COUNT(*) FROM ot WHERE numero IS NOT NULL AND fecha IS NOT NULL AND cliente IS NOT NULL")
        migrated_count = cursor.fetchone()[0]
        
        # Confirmar los cambios
        conn.commit()
        
        print(f"✅ Migración completada exitosamente.")
        print(f"📊 Registros migrados: {migrated_count}")
        
        # Crear índice en numero si es necesario
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_ot_numero ON ot(numero)")
            conn.commit()
            print("✅ Índice creado en la columna 'numero'")
        except Exception as e:
            print(f"⚠️  Advertencia al crear índice: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_migration():
    """Verifica que la migración se haya realizado correctamente"""
    
    db_path = "sql_app.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estructura de la tabla
        cursor.execute("PRAGMA table_info(ot)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_columns = ['numero', 'fecha', 'cliente', 'tipo', 'tecnico']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Faltan columnas: {', '.join(missing_columns)}")
            return False
        
        # Verificar datos
        cursor.execute("SELECT COUNT(*) FROM ot")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ot WHERE numero IS NOT NULL AND fecha IS NOT NULL AND cliente IS NOT NULL")
        valid_count = cursor.fetchone()[0]
        
        print(f"✅ Verificación completada:")
        print(f"   - Total de registros: {total_count}")
        print(f"   - Registros con datos válidos: {valid_count}")
        print(f"   - Columnas requeridas presentes: {', '.join(required_columns)}")
        
        return total_count == valid_count
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 MIGRACIÓN DE TABLA OT PARA FRONTEND")
    print("=" * 60)
    
    if migrate_ot_table():
        print("\n" + "=" * 60)
        print("🔍 VERIFICANDO MIGRACIÓN")
        print("=" * 60)
        
        if verify_migration():
            print("\n✅ ¡Migración completada exitosamente!")
            print("📝 La tabla OT ahora es compatible con el frontend.")
        else:
            print("\n⚠️  La migración se completó pero hay problemas en los datos.")
            sys.exit(1)
    else:
        print("\n❌ La migración falló.")
        sys.exit(1)
