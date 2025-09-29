#!/usr/bin/env python3
"""
Generador de archivos XLS/XLSX de prueba para testing del sistema de migraciones
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
import os

def generate_random_string(length=10):
    """Genera una cadena aleatoria de longitud especificada"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_date():
    """Genera una fecha aleatoria entre 2020 y 2025"""
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 12, 31)
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def generate_large_excel_file(target_size_mb=500, filename="test_file_500mb.xlsx"):
    """
    Genera un archivo Excel de gran tamaño para testing
    
    Args:
        target_size_mb (int): Tamaño objetivo en MB
        filename (str): Nombre del archivo a generar
    """
    print(f"🔧 Generando archivo Excel de {target_size_mb}MB...")
    
    # Asegurar que el archivo tenga extensión .xlsx
    if not filename.endswith('.xlsx'):
        filename = filename.replace('.xls', '') + '.xlsx'
    
    # Calcular aproximadamente cuántas filas necesitamos
    # Estimación: cada fila con 15 columnas ≈ 300-400 bytes
    bytes_per_row = 350  # Estimación más precisa
    target_bytes = target_size_mb * 1024 * 1024
    estimated_rows = target_bytes // bytes_per_row
    
    print(f"📊 Filas estimadas necesarias: {estimated_rows:,}")
    
    # Para archivos muy grandes, generamos todo de una vez pero con menos filas
    # y más contenido por celda para alcanzar el tamaño objetivo
    chunk_size = min(estimated_rows, 100000)  # Máximo 100K filas por vez
    total_chunks = (estimated_rows // chunk_size) + 1
    
    print(f"⚙️ Generando en {total_chunks} chunk(s) de hasta {chunk_size:,} filas cada uno...")
    
    file_path = os.path.join(os.getcwd(), filename)
    all_data = []
    
    for chunk_num in range(total_chunks):
        print(f"⏳ Procesando chunk {chunk_num + 1}/{total_chunks}...")
        
        # Determinar cuántas filas generar en este chunk
        if chunk_num == total_chunks - 1:
            rows_in_chunk = estimated_rows - (chunk_num * chunk_size)
        else:
            rows_in_chunk = chunk_size
        
        if rows_in_chunk <= 0:
            break
        
        start_id = chunk_num * chunk_size + 1
        end_id = start_id + rows_in_chunk
        
        # Generar datos con más contenido para alcanzar el tamaño objetivo
        data = {
            'ID': range(start_id, end_id),
            'Nombre_Completo': [f"{generate_random_string(12)} {generate_random_string(15)} {generate_random_string(10)}" for _ in range(rows_in_chunk)],
            'Email_Corporativo': [f"{generate_random_string(15)}.{generate_random_string(10)}@{generate_random_string(12)}.empresa.com" for _ in range(rows_in_chunk)],
            'Telefono_Principal': [f"+52-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}" for _ in range(rows_in_chunk)],
            'Telefono_Secundario': [f"+52-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}" for _ in range(rows_in_chunk)],
            'Direccion_Completa': [f"Calle {generate_random_string(15)} #{random.randint(1,9999)}, Colonia {generate_random_string(12)}, Ciudad {generate_random_string(10)}" for _ in range(rows_in_chunk)],
            'Codigo_Postal_Extendido': [f"{random.randint(10000, 99999)}-{random.randint(1000,9999)}" for _ in range(rows_in_chunk)],
            'Fecha_Nacimiento_Completa': [generate_random_date().strftime('%Y-%m-%d %H:%M:%S') for _ in range(rows_in_chunk)],
            'Salario_Anual_Detallado': [f"${round(random.uniform(30000, 250000), 2):,.2f} MXN" for _ in range(rows_in_chunk)],
            'Departamento_Completo': [f"Departamento de {random.choice(['Ventas y Marketing', 'Tecnologías de la Información', 'Recursos Humanos y Desarrollo', 'Finanzas y Contabilidad', 'Operaciones y Logística'])}" for _ in range(rows_in_chunk)],
            'Estatus_Empleado': [random.choice(['Activo - Tiempo Completo', 'Activo - Medio Tiempo', 'Inactivo - Licencia', 'Inactivo - Suspendido', 'Terminado - Renuncia']) for _ in range(rows_in_chunk)],
            'Comentarios_Extensos': [f"Comentario detallado del empleado: {generate_random_string(80)}. Observaciones adicionales: {generate_random_string(60)}. Notas importantes: {generate_random_string(40)}." for _ in range(rows_in_chunk)],
            'Fecha_Ingreso_Detallada': [generate_random_date().strftime('%Y-%m-%d %H:%M:%S') for _ in range(rows_in_chunk)],
            'Puntuacion_Performance': [f"{round(random.uniform(1, 10), 2)}/10 - {random.choice(['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Mejorable'])}" for _ in range(rows_in_chunk)],
            'Historial_Proyectos': [f"Proyecto: {generate_random_string(20)}, Fecha: {generate_random_date().strftime('%Y-%m')}, Status: {random.choice(['Completado', 'En Progreso', 'Pausado'])}" for _ in range(rows_in_chunk)]
        }
        
        chunk_df = pd.DataFrame(data)
        all_data.append(chunk_df)
        
        # Verificar si necesitamos más datos para alcanzar el tamaño objetivo
        if chunk_num == 0:
            # Escribir el primer chunk para verificar tamaño
            temp_df = pd.concat(all_data, ignore_index=True)
            temp_df.to_excel(file_path, index=False, engine='openpyxl')
            current_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   📁 Tamaño después del chunk 1: {current_size_mb:.1f}MB")
            
            # Ajustar estimación si es necesario
            if current_size_mb > 0:
                size_per_chunk = current_size_mb
                chunks_needed = target_size_mb / size_per_chunk
                total_chunks = max(1, int(chunks_needed))
                print(f"   🔄 Reajustando: necesitamos aproximadamente {total_chunks} chunks")
    
    # Combinar todos los chunks y escribir el archivo final
    print("� Combinando todos los chunks...")
    final_df = pd.concat(all_data, ignore_index=True)
    
    print("💾 Escribiendo archivo final...")
    final_df.to_excel(file_path, index=False, engine='openpyxl')
    
    final_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    final_rows = len(final_df)
    
    print(f"\n🎉 Archivo generado exitosamente:")
    print(f"   📁 Archivo: {filename}")
    print(f"   📊 Tamaño: {final_size_mb:.1f}MB")
    print(f"   📈 Filas totales: {final_rows:,}")
    print(f"   📋 Columnas: 15")
    print(f"   🗂️ Ubicación: {file_path}")
    
    return file_path

def generate_multiple_sheets_file(target_size_mb=500, filename="test_multiple_sheets_500mb.xlsx"):
    """
    Genera un archivo Excel con múltiples hojas para testing
    """
    print(f"🔧 Generando archivo Excel con múltiples hojas de {target_size_mb}MB...")
    
    # Calcular filas por hoja para distribir el tamaño
    sheets = ['Empleados', 'Ventas', 'Productos', 'Clientes', 'Pedidos']
    bytes_per_row = 250
    target_bytes = target_size_mb * 1024 * 1024
    rows_per_sheet = (target_bytes // len(sheets)) // bytes_per_row
    
    print(f"📊 Generando {len(sheets)} hojas con ~{rows_per_sheet:,} filas cada una...")
    
    file_path = os.path.join(os.getcwd(), filename)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for i, sheet_name in enumerate(sheets):
            print(f"⏳ Generando hoja '{sheet_name}' ({i+1}/{len(sheets)})...")
            
            # Generar datos específicos por tipo de hoja
            if sheet_name == 'Empleados':
                data = {
                    'ID_Empleado': range(1, rows_per_sheet + 1),
                    'Nombre': [generate_random_string(12) for _ in range(rows_per_sheet)],
                    'Apellido': [generate_random_string(10) for _ in range(rows_per_sheet)],
                    'Email': [f"{generate_random_string(8)}@empresa.com" for _ in range(rows_per_sheet)],
                    'Departamento': [random.choice(['Ventas', 'Marketing', 'IT', 'RRHH']) for _ in range(rows_per_sheet)],
                    'Salario': [round(random.uniform(35000, 120000), 2) for _ in range(rows_per_sheet)],
                    'Fecha_Ingreso': [generate_random_date().strftime('%Y-%m-%d') for _ in range(rows_per_sheet)]
                }
            elif sheet_name == 'Ventas':
                data = {
                    'ID_Venta': range(1, rows_per_sheet + 1),
                    'ID_Empleado': [random.randint(1, 1000) for _ in range(rows_per_sheet)],
                    'ID_Cliente': [random.randint(1, 5000) for _ in range(rows_per_sheet)],
                    'Producto': [generate_random_string(15) for _ in range(rows_per_sheet)],
                    'Cantidad': [random.randint(1, 100) for _ in range(rows_per_sheet)],
                    'Precio_Unitario': [round(random.uniform(10, 1000), 2) for _ in range(rows_per_sheet)],
                    'Total': [round(random.uniform(50, 10000), 2) for _ in range(rows_per_sheet)],
                    'Fecha_Venta': [generate_random_date().strftime('%Y-%m-%d %H:%M:%S') for _ in range(rows_per_sheet)]
                }
            elif sheet_name == 'Productos':
                data = {
                    'ID_Producto': range(1, rows_per_sheet + 1),
                    'Nombre_Producto': [generate_random_string(20) for _ in range(rows_per_sheet)],
                    'Categoria': [random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros']) for _ in range(rows_per_sheet)],
                    'Precio': [round(random.uniform(5, 2000), 2) for _ in range(rows_per_sheet)],
                    'Stock': [random.randint(0, 1000) for _ in range(rows_per_sheet)],
                    'Descripcion': [generate_random_string(100) for _ in range(rows_per_sheet)]
                }
            elif sheet_name == 'Clientes':
                data = {
                    'ID_Cliente': range(1, rows_per_sheet + 1),
                    'Nombre': [generate_random_string(12) for _ in range(rows_per_sheet)],
                    'Apellido': [generate_random_string(10) for _ in range(rows_per_sheet)],
                    'Email': [f"{generate_random_string(10)}@gmail.com" for _ in range(rows_per_sheet)],
                    'Telefono': [f"{random.randint(100,999)}-{random.randint(1000,9999)}" for _ in range(rows_per_sheet)],
                    'Ciudad': [generate_random_string(8) for _ in range(rows_per_sheet)],
                    'Pais': [random.choice(['Mexico', 'España', 'Argentina', 'Colombia', 'Chile']) for _ in range(rows_per_sheet)]
                }
            else:  # Pedidos
                data = {
                    'ID_Pedido': range(1, rows_per_sheet + 1),
                    'ID_Cliente': [random.randint(1, 5000) for _ in range(rows_per_sheet)],
                    'Fecha_Pedido': [generate_random_date().strftime('%Y-%m-%d') for _ in range(rows_per_sheet)],
                    'Estado': [random.choice(['Pendiente', 'Procesando', 'Enviado', 'Entregado', 'Cancelado']) for _ in range(rows_per_sheet)],
                    'Total': [round(random.uniform(20, 5000), 2) for _ in range(rows_per_sheet)],
                    'Metodo_Pago': [random.choice(['Tarjeta', 'Efectivo', 'Transferencia', 'PayPal']) for _ in range(rows_per_sheet)]
                }
            
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            current_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   📁 Tamaño actual: {current_size_mb:.1f}MB")
    
    final_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    print(f"\n🎉 Archivo con múltiples hojas generado exitosamente:")
    print(f"   📁 Archivo: {filename}")
    print(f"   📊 Tamaño: {final_size_mb:.1f}MB")
    print(f"   📈 Hojas: {len(sheets)}")
    print(f"   🗂️ Ubicación: {file_path}")
    
    return file_path

def main():
    """Función principal para generar archivos de prueba"""
    print("🚀 Generador de archivos Excel para testing de migraciones")
    print("=" * 60)
    
    while True:
        print("\nOpciones disponibles:")
        print("1. Generar archivo Excel simple (1 hoja) de ~500MB")
        print("2. Generar archivo Excel con múltiples hojas de ~500MB")
        print("3. Generar archivo personalizado (especificar tamaño)")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == '1':
            filename = input("Nombre del archivo (ej: test_500mb.xlsx): ").strip() or "test_500mb.xlsx"
            generate_large_excel_file(500, filename)
            
        elif choice == '2':
            filename = input("Nombre del archivo (ej: test_multiples_hojas_500mb.xlsx): ").strip() or "test_multiples_hojas_500mb.xlsx"
            generate_multiple_sheets_file(500, filename)
            
        elif choice == '3':
            try:
                size_mb = int(input("Tamaño en MB (ej: 1000): ").strip())
                filename = input("Nombre del archivo: ").strip()
                sheets = input("¿Múltiples hojas? (s/n): ").strip().lower() == 's'
                
                if sheets:
                    generate_multiple_sheets_file(size_mb, filename)
                else:
                    generate_large_excel_file(size_mb, filename)
            except ValueError:
                print("❌ Error: Ingresa un número válido para el tamaño")
                
        elif choice == '4':
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()