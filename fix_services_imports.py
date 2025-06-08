#!/usr/bin/env python3
"""
Script específico para corregir los imports restantes en la carpeta Services
que están causando errores tipo 'ModuleNotFoundError: No module named sql_app.Services.db'
"""

import os
import re
import glob

def fix_services_imports():
    """Corrige los imports problemáticos en la carpeta Services."""
    
    # Buscar todos los archivos Python en Services
    services_files = []
    for root, dirs, files in os.walk('sql_app/Services'):
        for file in files:
            if file.endswith('.py'):
                services_files.append(os.path.join(root, file))
    
    print(f"🔍 Encontrados {len(services_files)} archivos en Services")
    
    fixed_count = 0
    for file_path in services_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Calcular la profundidad desde sql_app/Services/
            relative_path = os.path.relpath(file_path, 'sql_app/Services')
            depth = len(relative_path.split(os.sep)) - 1
            dots = '.' * (depth + 3)  # +3 para llegar a sql_app desde Services
            
            # Patrones de corrección específicos para Services
            patterns = [
                # Corregir imports de db desde Services
                (r'from \.\.\.db\.database', f'from {dots}db.database'),
                (r'from \.\.\.db\.', f'from {dots}db.'),
                (r'from \.\.db\.database', f'from {dots}db.database'),
                (r'from \.\.db\.', f'from {dots}db.'),
                
                # Corregir imports dobles de Services
                (r'from \.\.Services\.', 'from ..'),
                (r'from \.\.\.Services\.', 'from ...'),
                
                # Corregir imports directos problemáticos
                (r'from db\.', f'from {dots}db.'),
                (r'from Services\.', 'from ..'),
            ]
            
            # Aplicar correcciones
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Correcciones específicas adicionales
            content = re.sub(r'from sql_app\.Services\.db\.', f'from {dots}db.', content)
            content = re.sub(r'from sql_app\.Services\.Services\.', 'from ..', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Corregido: {file_path}")
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
    
    print(f"\n✅ Proceso completado. {fixed_count} archivos en Services fueron corregidos.")

if __name__ == "__main__":
    if not os.path.exists('sql_app/Services'):
        print("❌ No se encontró el directorio sql_app/Services. Ejecuta desde el directorio raíz del proyecto.")
    else:
        fix_services_imports()
        print("🚀 Intenta ejecutar la aplicación nuevamente con: uvicorn sql_app.main:app --reload")
