#!/usr/bin/env python3
"""
Generador simple y rápido de archivos Excel de prueba
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random
import string
import os

def generate_simple_test_file(size_mb=500):
    """Genera un archivo de prueba de manera más eficiente"""
    print(f"🚀 Generando archivo de prueba de {size_mb}MB...")
    
    # Calcular filas necesarias (estimación más precisa)
    # Cada fila con 10 columnas variadas ≈ 150-200 bytes
    bytes_per_row = 180
    target_bytes = size_mb * 1024 * 1024
    num_rows = target_bytes // bytes_per_row
    
    print(f"📊 Generando {num_rows:,} filas...")
    
    # Generar datos de forma más eficiente
    np.random.seed(42)  # Para reproducibilidad
    
    # Crear arrays grandes de una vez
    ids = np.arange(1, num_rows + 1)
    names = [''.join(random.choices(string.ascii_letters, k=10)) for _ in range(num_rows)]
    emails = [f"user{i}@empresa.com" for i in range(1, num_rows + 1)]
    
    # Usar numpy para generar datos numéricos más rápido
    salaries = np.random.uniform(30000, 120000, num_rows).round(2)
    ages = np.random.randint(18, 65, num_rows)
    departments = np.random.choice(['Ventas', 'Marketing', 'IT', 'RRHH', 'Finanzas'], num_rows)
    
    # Fechas aleatorias
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = (end_date - start_date).days
    random_dates = [start_date + pd.Timedelta(days=int(np.random.randint(0, date_range))) for _ in range(num_rows)]
    
    # Crear DataFrame
    data = {
        'ID': ids,
        'Nombre': names,
        'Email': emails,
        'Edad': ages,
        'Salario': salaries,
        'Departamento': departments,
        'Fecha_Ingreso': random_dates,
        'Activo': np.random.choice([True, False], num_rows),
        'Puntuacion': np.random.uniform(1, 10, num_rows).round(1),
        'Comentarios': [f"Comentario del empleado número {i}" for i in range(1, num_rows + 1)]
    }
    
    print("📝 Creando DataFrame...")
    df = pd.DataFrame(data)
    
    # Guardar archivo
    filename = f"test_file_{size_mb}mb.xlsx"
    file_path = os.path.join(os.getcwd(), filename)
    
    print("💾 Guardando archivo...")
    df.to_excel(file_path, index=False, engine='openpyxl')
    
    # Verificar tamaño final
    final_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    print(f"\n✅ Archivo generado:")
    print(f"   📁 Nombre: {filename}")
    print(f"   📊 Tamaño: {final_size_mb:.1f}MB")
    print(f"   📈 Filas: {len(df):,}")
    print(f"   📋 Columnas: {len(df.columns)}")
    print(f"   🗂️ Ubicación: {file_path}")
    
    return file_path

if __name__ == "__main__":
    # Generar archivo de 500MB
    generate_simple_test_file(500)