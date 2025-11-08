#!/usr/bin/env python3
"""
Script para agregar la columna metodo_pago a la tabla ecomerce_pedidos
"""

import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_connection_string():
    """Obtener la cadena de conexión desde las variables de entorno"""
    server = os.getenv('DB_SERVER', 'localhost')
    database = os.getenv('DB_NAME', 'ecommerce')
    username = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', 'YourPassword123!')
    driver = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')

    return f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def agregar_columna_metodo_pago():
    """Agregar la columna metodo_pago a la tabla ecomerce_pedidos"""

    connection_string = get_connection_string()

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'ecomerce_pedidos' AND COLUMN_NAME = 'metodo_pago'
        """)

        if cursor.fetchone():
            print("✅ La columna 'metodo_pago' ya existe en la tabla 'ecomerce_pedidos'")
            return True

        # SQL para agregar la columna metodo_pago
        alter_table_sql = """
        ALTER TABLE ecomerce_pedidos
        ADD metodo_pago NVARCHAR(50) DEFAULT 'efectivo'
        """

        print("Agregando columna 'metodo_pago' a la tabla de pedidos...")
        cursor.execute(alter_table_sql)
        conn.commit()

        print("✅ Columna 'metodo_pago' agregada exitosamente")

        # Verificar que la columna se agregó correctamente
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'ecomerce_pedidos' AND COLUMN_NAME = 'metodo_pago'
        """)

        column_info = cursor.fetchone()
        if column_info:
            print(f"📊 Información de la columna agregada:")
            print(f"   - Nombre: {column_info[0]}")
            print(f"   - Tipo: {column_info[1]}")
            print(f"   - Nullable: {column_info[2]}")
            print(f"   - Default: {column_info[3]}")

    except pyodbc.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

    return True

def verificar_tabla_actualizada():
    """Verificar que la tabla tiene la nueva columna"""

    connection_string = get_connection_string()

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar columnas
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'ecomerce_pedidos'
            ORDER BY ORDINAL_POSITION
        """)

        columns = cursor.fetchall()
        print("📋 Columnas actualizadas de la tabla 'ecomerce_pedidos':")
        for col in columns:
            default_value = f" (DEFAULT: {col[3]})" if col[3] else ""
            print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'}){default_value}")

    except pyodbc.Error as e:
        print(f"❌ Error al verificar tabla: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando actualización de tabla ecomerce_pedidos...")
    print("=" * 60)

    if agregar_columna_metodo_pago():
        print("\n🔍 Verificando tabla actualizada...")
        verificar_tabla_actualizada()
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el proceso de actualización de tabla")