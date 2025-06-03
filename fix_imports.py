#!/usr/bin/env python3
"""
Script para corregir automáticamente las importaciones problemáticas
en toda la aplicación FastAPI.
"""

import os
import re
import glob

def fix_imports_in_file(file_path):
    """Corrige las importaciones en un archivo específico."""
    print(f"Procesando: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de importaciones problemáticas y sus reemplazos
        patterns = [
            # Services imports
            (r'^from Services\.', 'try:\n    from ...Services.', 'except ImportError:\n    from sql_app.Services.'),
            # db imports  
            (r'^from db\.', 'try:\n    from ...db.', 'except ImportError:\n    from sql_app.db.'),
        ]
        
        # Verificar si el archivo ya tiene try/catch para importaciones
        if 'try:' in content and 'from ...Services.' in content:
            print(f"  ✓ Ya tiene importaciones corregidas")
            return False
            
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Buscar importaciones problemáticas
            if re.match(r'^from (Services|db)\.', line.strip()):
                # Extraer el resto de la importación
                import_line = line.strip()
                
                # Buscar todas las líneas relacionadas con esta importación
                import_lines = [import_line]
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().endswith(',') or lines[j].strip().startswith('from')):
                    if lines[j].strip():
                        import_lines.append(lines[j].strip())
                    j += 1
                
                # Crear la versión corregida
                if import_line.startswith('from Services.'):
                    relative_import = import_line.replace('from Services.', 'from ...Services.')
                    absolute_import = import_line.replace('from Services.', 'from sql_app.Services.')
                elif import_line.startswith('from db.'):
                    relative_import = import_line.replace('from db.', 'from ...db.')
                    absolute_import = import_line.replace('from db.', 'from sql_app.db.')
                
                # Agregar las líneas corregidas
                new_lines.extend([
                    'try:',
                    f'    {relative_import}',
                    'except ImportError:',
                    f'    {absolute_import}'
                ])
                
                i = j - 1  # Avanzar hasta después de las líneas procesadas
            else:
                new_lines.append(line)
            
            i += 1
        
        new_content = '\n'.join(new_lines)
        
        # Solo escribir si hubo cambios
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ Corregido")
            return True
        else:
            print(f"  - Sin cambios necesarios")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Procesa todos los archivos Python en el proyecto."""
    base_path = "sql_app"
    
    # Buscar todos los archivos Python
    python_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Encontrados {len(python_files)} archivos Python")
    print("=" * 50)
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print("=" * 50)
    print(f"Archivos corregidos: {fixed_count}/{len(python_files)}")

if __name__ == "__main__":
    main()
