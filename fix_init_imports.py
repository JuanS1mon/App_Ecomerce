#!/usr/bin/env python3
"""
Script para corregir imports en archivos __init__.py
Convierte imports relativos problemáticos a imports absolutos
"""

import os
import re

def fix_init_imports(filepath):
    """Corrige los imports en un archivo __init__.py"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar imports relativos problemáticos
        # Ejemplo: from Services.app_stock.xxx import yyy
        pattern = r'from Services\.'
        
        if re.search(pattern, content):
            print(f"Corrigiendo: {filepath}")
            
            # Reemplazar "from Services." con "from sql_app.Services."
            fixed_content = re.sub(r'from Services\.', 'from sql_app.Services.', content)
            
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
    base_path = "sql_app/Services"
    init_files = []
    
    # Buscar todos los archivos __init__.py
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == "__init__.py":
                init_files.append(os.path.join(root, file))
    
    print(f"Encontrados {len(init_files)} archivos __init__.py")
    
    corrected_count = 0
    for filepath in init_files:
        if fix_init_imports(filepath):
            corrected_count += 1
    
    print(f"\n🎉 Proceso completado. {corrected_count} archivos corregidos de {len(init_files)} total.")

if __name__ == "__main__":
    main()
