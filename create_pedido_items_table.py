#!/usr/bin/env python3
"""
Script para crear la tabla de pedido_items en la base de datos SQL Server
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

def crear_tabla_pedido_items():
    """Crear la tabla de pedido_items"""

    connection_string = get_connection_string()

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # SQL para crear la tabla de pedido_items
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ecomerce_pedido_items' AND xtype='U')
        CREATE TABLE ecomerce_pedido_items (
            id INT IDENTITY(1,1) PRIMARY KEY,
            id_pedido INT NOT NULL,
            id_producto INT NOT NULL,
            cantidad INT NOT NULL,
            precio_unitario FLOAT NOT NULL,
            nombre_producto NVARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (id_pedido) REFERENCES ecomerce_pedidos(id)
        )
        """

        print("Creando tabla de pedido_items...")
        cursor.execute(create_table_sql)
        conn.commit()

        print("✅ Tabla 'ecomerce_pedido_items' creada exitosamente")

        # Verificar que la tabla se creó correctamente
        cursor.execute("SELECT COUNT(*) FROM ecomerce_pedido_items")
        count = cursor.fetchone()[0]
        print(f"📊 Registros actuales en la tabla: {count}")

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

def verificar_tabla():
    """Verificar que la tabla existe y tiene la estructura correcta"""

    connection_string = get_connection_string()

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar que la tabla existe
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'ecomerce_pedido_items'
        """)

        if cursor.fetchone():
            print("✅ La tabla 'ecomerce_pedido_items' existe")

            # Verificar columnas
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'ecomerce_pedido_items'
                ORDER BY ORDINAL_POSITION
            """)

            columns = cursor.fetchall()
            print("📋 Columnas de la tabla:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")

        else:
            print("❌ La tabla 'ecomerce_pedido_items' no existe")

    except pyodbc.Error as e:
        print(f"❌ Error al verificar tabla: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando creación de tabla de pedido_items...")
    print("=" * 50)

    if crear_tabla_pedido_items():
        print("\n🔍 Verificando tabla creada...")
        verificar_tabla()
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el proceso de creación de tabla")