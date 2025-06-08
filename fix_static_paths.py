#!/usr/bin/env python3
"""
Script para corregir todas las rutas estáticas incorrectas en el proyecto FastAPI.
Cambia todas las referencias de "sql_app/static/" a "sql_app/static/" y 
corrige las configuraciones de Jinja2Templates.
"""

import os
import re
from pathlib import Path

def fix_file_paths(file_path: str) -> bool:
    """
    Corrige las rutas estáticas en un archivo específico.
    Retorna True si se realizaron cambios, False en caso contrario.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # 1. Corregir rutas de archivos estáticos: "sql_app/static/" -> "sql_app/static/"
        # Patrón para detectar rutas que empiecen con "sql_app/static/" pero no "sql_app/static/"
        static_pattern = r'(?<!sql_app/)"sql_app/static/'
        content = re.sub(static_pattern, '"sql_app/static/', content)
        
        # 2. Corregir configuraciones de Jinja2Templates
        # Cambiar directory="static" por directory="sql_app/static"
        jinja_pattern1 = r'Jinja2Templates\(directory="static"\)'
        content = re.sub(jinja_pattern1, 'Jinja2Templates(directory="sql_app/static")', content)
        
        # Cambiar directory="sql_app/static/html" por directory="sql_app/static"
        jinja_pattern2 = r'Jinja2Templates\(directory="sql_app/static/html"\)'
        content = re.sub(jinja_pattern2, 'Jinja2Templates(directory="sql_app/static")', content)
        
        # 3. Corregir referencias de archivos con open() que usen f-strings
        # Patrón para f"sql_app/static/... -> f"sql_app/static/...
        fstring_pattern = r'f"sql_app/static/'
        content = re.sub(fstring_pattern, 'f"sql_app/static/', content)
        
        # Si hubo cambios, guardar el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def find_python_files(directory: str) -> list:
    """Encuentra todos los archivos .py en el directorio y subdirectorios."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    """Función principal que ejecuta la corrección masiva."""
    # Directorio base del proyecto
    base_dir = "c:/Users/PCJuan/Desktop/sql_app"
    
    print("🔧 Iniciando corrección masiva de rutas estáticas...")
    print(f"📁 Directorio base: {base_dir}")
    
    # Encontrar todos los archivos Python
    python_files = find_python_files(base_dir)
    print(f"📄 Archivos Python encontrados: {len(python_files)}")
    
    # Procesar cada archivo
    files_changed = 0
    files_processed = 0
    
    for file_path in python_files:
        files_processed += 1
        if fix_file_paths(file_path):
            files_changed += 1
            relative_path = os.path.relpath(file_path, base_dir)
            print(f"✅ Corregido: {relative_path}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos procesados: {files_processed}")
    print(f"   - Archivos modificados: {files_changed}")
    print(f"   - Archivos sin cambios: {files_processed - files_changed}")
    
    if files_changed > 0:
        print(f"\n🎉 ¡Corrección completada! Se corrigieron {files_changed} archivos.")
        print("🚀 Ahora puedes probar tu aplicación FastAPI.")
    else:
        print("\n✨ No se encontraron archivos que necesiten corrección.")

if __name__ == "__main__":
    main()
