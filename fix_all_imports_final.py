#!/usr/bin/env python3
"""
Script para arreglar todos los imports relativos problemáticos en el proyecto
"""

import os
import re

def fix_imports_in_file(file_path):
    """Corregir imports en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de corrección para imports relativos
        patterns = [
            # Tres puntos hacia dos puntos
            (r'from \.\.\.db\.', 'from db.'),
            (r'from \.\.\.Services\.', 'from Services.'),
            (r'from \.\.\.routers\.', 'from routers.'),
            
            # Dos puntos hacia un solo nivel
            (r'from \.\.db\.', 'from db.'),
            (r'from \.\.Services\.', 'from Services.'),
            (r'from \.\.routers\.', 'from routers.'),
            
            # Un punto hacia absoluto
            (r'from \.db\.', 'from db.'),
            (r'from \.Services\.', 'from Services.'),
            (r'from \.routers\.', 'from routers.'),
            
            # Imports específicos problemáticos
            (r'from sql_app\.db\.database', 'from db.database'),
            (r'from sql_app\.db\.', 'from db.'),
            (r'from sql_app\.Services\.', 'from Services.'),
            (r'from sql_app\.routers\.', 'from routers.'),
        ]
        
        # Aplicar correcciones
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Eliminar bloques try-except problemáticos de imports
        # Buscar patrones como:
        # try:
        #     from ...
        # except ImportError:
        #     from ...
        
        try_except_pattern = r'try:\s*\n(\s+from [^\n]+\n)+except ImportError:\s*\n(\s+from [^\n]+\n)+'
        matches = re.finditer(try_except_pattern, content, re.MULTILINE)
        
        for match in matches:
            # Extraer solo la primera parte del try
            try_block = match.group(0)
            lines = try_block.split('\n')
            
            # Encontrar las líneas de import del bloque try
            import_lines = []
            in_try = False
            for line in lines:
                if line.strip() == 'try:':
                    in_try = True
                elif line.strip().startswith('except'):
                    break
                elif in_try and line.strip().startswith('from'):
                    # Remover la indentación extra
                    clean_line = line.lstrip()
                    import_lines.append(clean_line)
            
            if import_lines:
                replacement_text = '\n'.join(import_lines)
                content = content.replace(match.group(0), replacement_text)
        
        # Si el contenido cambió, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corregido: {file_path}")
            return True
        else:
            print(f"➖ Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 ARREGLANDO IMPORTS RELATIVOS EN TODO EL PROYECTO")
    print("=" * 60)
    
    # Directorio base del proyecto
    base_dir = r"c:\Users\PCJuan\Desktop\sql_app\sql_app"
    
    # Buscar todos los archivos Python
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"📁 Encontrados {len(python_files)} archivos Python")
    
    # Procesar cada archivo
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Proceso completado: {fixed_count} archivos corregidos")
    
    if fixed_count > 0:
        print("\n🔄 Ahora intenta iniciar el servidor:")
        print("cd c:\\Users\\PCJuan\\Desktop\\sql_app\\sql_app")
        print("uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main()
