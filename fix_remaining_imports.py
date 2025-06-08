#!/usr/bin/env python3
"""
Script para corregir automáticamente todos los imports problemáticos restantes
que están causando ModuleNotFoundError en la aplicación FastAPI.
"""

import os
import re
import glob

def fix_imports_in_file(file_path):
    """Arregla los imports en un archivo específico."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Determinar la profundidad del archivo para calcular los imports relativos correctos
        # Contar cuántos niveles está desde sql_app/
        relative_path = os.path.relpath(file_path, 'sql_app')
        depth = len(relative_path.split(os.sep)) - 1
        
        # Para archivos en routers/config/
        if 'routers/config' in file_path or 'routers\\config' in file_path:
            # Patterns para routers/config/
            patterns = [
                (r'from \.\.Services\.', 'from ...Services.'),
                (r'from \.\.db\.', 'from ...db.'),
                (r'from Services\.', 'from ...Services.'),
                (r'from db\.', 'from ...db.'),
                (r'from routers\.', 'from ...routers.'),
            ]
        # Para archivos en Services/
        elif 'Services' in file_path:
            patterns = [
                (r'from \.\.db\.', 'from ...db.'),
                (r'from db\.', 'from ...db.'),
                (r'from \.\.Services\.', 'from ..Services.'),
                (r'from Services\.', 'from ..Services.'),
            ]
        # Para archivos en db/models/
        elif 'db/models' in file_path or 'db\\models' in file_path:
            patterns = [
                (r'from \.\.\.db\.database', 'from ...database'),
                (r'from \.\.\.db\.', 'from ...'),
                (r'from db\.', 'from ...'),
            ]
        # Para archivos en db/crud/
        elif 'db/crud' in file_path or 'db\\crud' in file_path:
            patterns = [
                (r'from \.\.\.db\.database', 'from ...database'),
                (r'from \.\.\.db\.', 'from ...'),
                (r'from db\.', 'from ...'),
            ]
        # Para archivos en db/schemas/
        elif 'db/schemas' in file_path or 'db\\schemas' in file_path:
            patterns = [
                (r'from \.\.\.db\.database', 'from ...database'),
                (r'from \.\.\.db\.', 'from ...'),
                (r'from db\.', 'from ...'),
            ]
        else:
            # Patterns generales
            patterns = [
                (r'from Services\.', 'from .Services.'),
                (r'from db\.', 'from .db.'),
                (r'from routers\.', 'from .routers.'),
            ]
        
        # Aplicar todas las correcciones
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Correcciones específicas adicionales
        content = re.sub(r'from sql_app\.routers\.Services\.', 'from ...Services.', content)
        content = re.sub(r'from sql_app\.routers\.db\.', 'from ...db.', content)
        content = re.sub(r'from sql_app\.Services\.db\.', 'from ...db.', content)
        content = re.sub(r'from sql_app\.db\.db\.', 'from ...db.', content)
        
        # Corregir imports de security_improved a security
        content = re.sub(r'security_improved', 'security', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corregido: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal que recorre todos los archivos Python y corrige los imports."""
    
    if not os.path.exists('sql_app'):
        print("❌ No se encontró el directorio sql_app. Ejecuta desde el directorio raíz del proyecto.")
        return
    
    # Buscar todos los archivos Python en sql_app
    python_files = []
    for root, dirs, files in os.walk('sql_app'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 Encontrados {len(python_files)} archivos Python")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Proceso completado. {fixed_count} archivos fueron corregidos.")
    print("🚀 Intenta ejecutar la aplicación nuevamente con: uvicorn sql_app.main:app --reload")

if __name__ == "__main__":
    main()
