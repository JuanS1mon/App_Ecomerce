#!/usr/bin/env python3
"""
Script para corregir ALL imports problemáticos en el proyecto
Convierte todos los imports relativos problemáticos a imports absolutos
"""

import os
import re
import glob

def fix_all_imports(filepath):
    """Corrige los imports en cualquier archivo Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrones para encontrar imports relativos problemáticos
        patterns = [
            (r'from Services\.', 'from sql_app.Services.'),  # from Services. -> from sql_app.Services.
            (r'from \.\.\.Services\.', 'from sql_app.Services.'),  # from ...Services. -> from sql_app.Services.
            (r'from \.\.Services\.', 'from sql_app.Services.'),   # from ..Services. -> from sql_app.Services.
        ]
        
        changed = False
        fixed_content = content
        
        for pattern, replacement in patterns:
            if re.search(pattern, fixed_content):
                print(f"Corrigiendo patrón '{pattern}' en: {filepath}")
                fixed_content = re.sub(pattern, replacement, fixed_content)
                changed = True
        
        if changed:
            # Escribir el archivo corregido
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"✅ Corregido: {filepath}")
            return True
        else:
            print(f"Sin cambios necesarios: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False

def main():
    """Función principal"""
    # Buscar todos los archivos Python en Services
    python_files = []
    for root, dirs, files in os.walk("sql_app/Services"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Encontrados {len(python_files)} archivos Python en Services/")
    
    corrected_count = 0
    for filepath in python_files:
        if fix_all_imports(filepath):
            corrected_count += 1
    
    print(f"\n🎉 Proceso completado. {corrected_count} archivos corregidos de {len(python_files)} total.")

if __name__ == "__main__":
    main()
