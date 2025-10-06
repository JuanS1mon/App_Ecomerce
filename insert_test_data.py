#!/usr/bin/env python3
"""
Script para insertar datos de prueba en tablas vacías
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

from sqlalchemy import text
from sql_app.db.database import engine

def insert_test_data():
    """Insertar datos de prueba en algunas tablas"""
    try:
        print("🔧 INSERTANDO DATOS DE PRUEBA")
        print("=" * 40)
        
        with engine.connect() as conn:
            # Insertar datos en la tabla articulos
            print("📦 Insertando datos en tabla 'articulos'...")
            
            # Primero verificar la estructura de la tabla
            schema_query = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'articulos'
            ORDER BY ORDINAL_POSITION
            """
            schema_result = conn.execute(text(schema_query))
            columns = schema_result.fetchall()
            
            print("🏗️ Estructura de tabla 'articulos':")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Insertar algunos registros de prueba con las columnas correctas
            insert_queries = [
                """
                INSERT INTO articulos (codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo)
                VALUES ('ART001', 'Producto Demo 1 - Explorador de Tablas', 20.00, 29.99, 'MOD001', 'Marca Demo', 'TIPO1')
                """,
                """
                INSERT INTO articulos (codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo)
                VALUES ('ART002', 'Producto Demo 2 - Sistema de Stock', 30.00, 45.50, 'MOD002', 'Marca Demo', 'TIPO2')
                """,
                """
                INSERT INTO articulos (codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo)
                VALUES ('ART003', 'Producto Demo 3 - Gestión Inventario', 8.00, 12.75, 'MOD003', 'Marca Demo', 'TIPO1')
                """,
                """
                INSERT INTO articulos (codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo, codigo_barras)
                VALUES ('ART004', 'Producto Demo 4 - Con Código de Barras', 15.00, 22.99, 'MOD004', 'Marca Premium', 'TIPO3', '1234567890123')
                """,
                """
                INSERT INTO articulos (codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo, qr_data)
                VALUES ('ART005', 'Producto Demo 5 - Con QR', 25.00, 39.99, 'MOD005', 'Marca Tech', 'TIPO2', '{"producto":"ART005","info":"demo"}')
                """
            ]
            
            for i, query in enumerate(insert_queries, 1):
                try:
                    conn.execute(text(query))
                    print(f"✅ Registro {i} insertado")
                except Exception as e:
                    print(f"⚠️ Error insertando registro {i}: {e}")
            
            # Confirmar cambios
            conn.commit()
            
            # Verificar que se insertaron
            count_result = conn.execute(text("SELECT COUNT(*) FROM articulos"))
            total = count_result.scalar()
            print(f"📊 Total de registros en 'articulos': {total}")
            
            # Mostrar algunos registros
            if total > 0:
                sample_result = conn.execute(text("SELECT TOP 3 codigo, descripcion, precioventa FROM articulos"))
                print("\n📋 Primeros registros insertados:")
                for row in sample_result:
                    print(f"  - {row[0]}: {row[1]} (${row[2]})")
        
        print("\n✅ Datos de prueba insertados correctamente")
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insert_test_data()