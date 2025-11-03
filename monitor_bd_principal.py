"""
Script para monitorear en tiempo real las tablas en la BD Principal
Ejecutar este script ANTES de hacer la importación para ver si se crea la tabla
"""
import os
import sys
from dotenv import load_dotenv
import pyodbc
import time

# Cargar variables de entorno
load_dotenv()

# Configuración de BD Principal desde .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "tecnolarUnificado")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

print("=" * 80)
print("🔍 MONITOR DE BASE DE DATOS PRINCIPAL")
print("=" * 80)
print(f"📊 BD Principal: {DB_NAME}")
print(f"🖥️  Servidor: {DB_HOST}")
print(f"👤 Usuario: {DB_USER}")
print("=" * 80)
print()

# Construir connection string
conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_HOST};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"

try:
    # Conectar a BD principal
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("✅ Conexión exitosa a BD Principal")
    print()
    print("🔄 Monitoreando tablas con 'migrado' en el nombre cada 3 segundos...")
    print("   Presiona Ctrl+C para detener")
    print()
    print("-" * 80)
    
    tablas_anteriores = set()
    
    while True:
        # Consultar tablas con "migrado" en el nombre
        query = """
        SELECT 
            t.name as tabla_nombre,
            p.rows as total_registros,
            (SELECT COUNT(*) FROM sys.columns WHERE object_id = t.object_id) as total_columnas
        FROM sys.tables t
        INNER JOIN sys.partitions p ON t.object_id = p.object_id
        WHERE p.index_id IN (0,1)
        AND t.name LIKE '%migrado%'
        ORDER BY t.name
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        tablas_actuales = {row.tabla_nombre for row in resultados}
        
        # Detectar nuevas tablas
        nuevas_tablas = tablas_actuales - tablas_anteriores
        
        if nuevas_tablas:
            print(f"\n🆕 ¡NUEVA TABLA DETECTADA! {time.strftime('%H:%M:%S')}")
            for tabla in nuevas_tablas:
                print(f"   ✨ {tabla}")
        
        # Mostrar estado actual
        print(f"\r⏰ {time.strftime('%H:%M:%S')} | Tablas: {len(tablas_actuales)}", end="", flush=True)
        
        if resultados and (nuevas_tablas or len(tablas_actuales) != len(tablas_anteriores)):
            print("\n")
            print(f"📋 TABLAS ACTUALES EN BD PRINCIPAL ({len(tablas_actuales)}):")
            print("-" * 80)
            for i, row in enumerate(resultados, 1):
                indicador = "🆕" if row.tabla_nombre in nuevas_tablas else "  "
                print(f"{indicador} {i}. {row.tabla_nombre:<50} | {row.total_registros:>6} registros | {row.total_columnas:>3} columnas")
            print("-" * 80)
        
        tablas_anteriores = tablas_actuales
        time.sleep(3)
        
except pyodbc.Error as e:
    print(f"\n❌ ERROR de conexión a BD Principal:")
    print(f"   {str(e)}")
    print()
    print("📋 Connection String usado:")
    print(f"   {conn_str.replace(DB_PASSWORD, '****')}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n⏹️  Monitor detenido por usuario")
    print("=" * 80)
    cursor.close()
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"\n❌ ERROR inesperado:")
    print(f"   {str(e)}")
    sys.exit(1)
