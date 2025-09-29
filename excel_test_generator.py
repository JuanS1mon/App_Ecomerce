#!/usr/bin/env python3
"""
Generador de archivos Excel respetando los límites de Excel
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random
import string
import os

def generate_realistic_test_file(target_size_mb=100):
    """Genera un archivo de prueba respetando límites de Excel"""
    print(f"🚀 Generando archivo de prueba de ~{target_size_mb}MB...")
    
    # Límite de Excel: 1,048,576 filas máximo
    MAX_EXCEL_ROWS = 1048576
    
    # Calcular filas óptimas
    # Con más columnas y contenido más largo por celda para alcanzar el tamaño
    num_rows = min(MAX_EXCEL_ROWS - 1, 800000)  # Usar menos filas pero más contenido
    
    print(f"📊 Generando {num_rows:,} filas con contenido extendido...")
    
    # Generar datos con más contenido por celda
    np.random.seed(42)
    
    def generate_long_string(length):
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    # Crear datos con más contenido
    data = {
        'ID': np.arange(1, num_rows + 1),
        'Nombre_Completo': [f"{generate_long_string(15)} {generate_long_string(15)} {generate_long_string(10)}" for _ in range(num_rows)],
        'Email_Corporativo': [f"{generate_long_string(12)}.{generate_long_string(8)}@empresa-ejemplo-muy-larga.com" for _ in range(num_rows)],
        'Telefono_Principal': [f"+52-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}" for _ in range(num_rows)],
        'Direccion_Completa': [f"Calle {generate_long_string(20)} Número {random.randint(1,9999)}, Colonia {generate_long_string(15)}, Ciudad {generate_long_string(12)}, Estado {generate_long_string(10)}" for _ in range(num_rows)],
        'Salario_Detallado': [f"${np.random.uniform(25000, 200000):.2f} MXN anuales más bonificaciones" for _ in range(num_rows)],
        'Departamento_Completo': [f"Departamento de {random.choice(['Ventas y Marketing Digital', 'Tecnologías de la Información y Sistemas', 'Recursos Humanos y Desarrollo Organizacional', 'Finanzas, Contabilidad y Auditoría', 'Operaciones, Logística y Cadena de Suministro'])}" for _ in range(num_rows)],
        'Fecha_Ingreso': [datetime(random.randint(2015, 2025), random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_rows)],
        'Estatus_Empleado': [random.choice(['Activo - Tiempo Completo Indefinido', 'Activo - Medio Tiempo por Contrato', 'Inactivo - Licencia por Maternidad', 'Inactivo - Suspendido Temporalmente', 'Terminado - Renuncia Voluntaria']) for _ in range(num_rows)],
        'Puntuacion_Performance': [f"{np.random.uniform(1, 10):.2f}/10.00 - Evaluación {random.choice(['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Necesita Mejora'])}" for _ in range(num_rows)],
        'Comentarios_Extensos': [f"Observaciones detalladas del empleado: {generate_long_string(100)}. Comentarios adicionales de supervisores: {generate_long_string(80)}. Notas de recursos humanos: {generate_long_string(60)}." for _ in range(num_rows)],
        'Proyectos_Asignados': [f"Proyecto: {generate_long_string(25)}, Fase: {random.choice(['Iniciación', 'Planificación', 'Ejecución', 'Monitoreo', 'Cierre'])}, Progreso: {random.randint(0,100)}%" for _ in range(num_rows)],
        'Certificaciones': [f"Certificación en {generate_long_string(30)}, Vigencia: {random.randint(2024, 2028)}, Institución: {generate_long_string(25)}" for _ in range(num_rows)],
        'Contacto_Emergencia': [f"Nombre: {generate_long_string(20)}, Teléfono: +52-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}, Relación: {random.choice(['Padre', 'Madre', 'Hermano', 'Hermana', 'Cónyuge', 'Hijo', 'Otro Familiar'])}" for _ in range(num_rows)],
        'Historial_Capacitaciones': [f"Capacitación: {generate_long_string(40)}, Fecha: {datetime(random.randint(2020, 2025), random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d')}, Duración: {random.randint(4, 40)} horas, Resultado: {random.choice(['Aprobado', 'Excelente', 'Satisfactorio'])}" for _ in range(num_rows)]
    }
    
    print("📝 Creando DataFrame...")
    df = pd.DataFrame(data)
    
    # Guardar archivo
    filename = f"test_file_{target_size_mb}mb_{num_rows}_rows.xlsx"
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
    
    # Verificar si es lo suficientemente grande para probar paralelismo
    if final_size_mb > 1.0:
        print(f"🚀 Este archivo activará el procesamiento PARALELO (>{1.0}GB)")
    else:
        print(f"⚙️ Este archivo usará procesamiento secuencial (<{1.0}GB)")
    
    return file_path

def generate_multiple_sizes():
    """Genera varios archivos de diferentes tamaños para testing"""
    sizes = [50, 100, 200]  # MB
    
    for size in sizes:
        print(f"\n{'='*60}")
        try:
            generate_realistic_test_file(size)
        except Exception as e:
            print(f"❌ Error generando archivo de {size}MB: {e}")
        print(f"{'='*60}")

if __name__ == "__main__":
    print("🎯 Generador de Archivos de Prueba para Migraciones")
    print("Opciones:")
    print("1. Archivo único de ~200MB")
    print("2. Múltiples archivos (50MB, 100MB, 200MB)")
    
    choice = input("\nSelecciona opción (1/2): ").strip()
    
    if choice == '2':
        generate_multiple_sizes()
    else:
        generate_realistic_test_file(200)