#!/usr/bin/env python3
"""
Script para agregar soporte de importaciones híbridas en todos los archivos
"""

import os
import re
import glob

def add_hybrid_imports(file_path):
    """Convierte importaciones relativas en importaciones híbridas (try/except)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Buscar todas las importaciones relativas que empiecen con puntos
        relative_imports = re.findall(r'^from \.+[\w.]+\s+import\s+[^#\n]+', content, re.MULTILINE)
        
        if not relative_imports:
            return False
        
        # Agrupar importaciones relativas consecutivas
        lines = content.split('\n')
        new_lines = []
        in_import_block = False
        import_block = []
        
        for line in lines:
            # Verificar si es una importación relativa
            if re.match(r'^from \.+[\w.]+\s+import\s+', line):
                if not in_import_block:
                    in_import_block = True
                    import_block = []
                import_block.append(line)
            else:
                # Si estábamos en un bloque de importaciones, procesarlo
                if in_import_block:
                    new_lines.extend(convert_import_block(import_block))
                    in_import_block = False
                    import_block = []
                new_lines.append(line)
        
        # Procesar el último bloque si existe
        if in_import_block:
            new_lines.extend(convert_import_block(import_block))
        
        new_content = '\n'.join(new_lines)
        
        # Solo escribir si hay cambios
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Corregido: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def convert_import_block(import_lines):
    """Convierte un bloque de importaciones relativas en un bloque try/except"""
    if not import_lines:
        return []
    
    result = ['try:']
    result.append('    # Importaciones relativas (cuando se ejecuta como módulo)')
    
    for line in import_lines:
        result.append(f'    {line}')
    
    result.append('except ImportError:')
    result.append('    # Importaciones absolutas (cuando se ejecuta directamente)')
    
    for line in import_lines:
        # Convertir importación relativa a absoluta
        absolute_line = convert_relative_to_absolute(line)
        result.append(f'    {absolute_line}')
    
    return result

def convert_relative_to_absolute(relative_import):
    """Convierte una importación relativa a absoluta"""
    # Ejemplo: "from ..db.database import get_db" -> "from db.database import get_db"
    # Ejemplo: "from ...Services.mail import mail" -> "from Services.mail import mail"
    
    # Remover los puntos del inicio
    pattern = r'^from \.+(.*)'
    match = re.match(pattern, relative_import)
    
    if match:
        module_path = match.group(1)
        return f'from {module_path}'
    
    return relative_import

def main():
    """Función principal"""
    base_path = r"c:\Users\PCJuan\Desktop\sql_app\sql_app"
    
    if not os.path.exists(base_path):
        print(f"❌ No se encuentra el directorio base: {base_path}")
        return
    
    print("🔧 Convirtiendo importaciones relativas a híbridas...")
    
    # Buscar todos los archivos .py en sql_app, excluyendo main.py
    pattern = os.path.join(base_path, "**", "*.py")
    python_files = glob.glob(pattern, recursive=True)
    
    fixed_count = 0
    total_count = 0
    
    for file_path in python_files:
        # Saltar archivos especiales y main.py (ya lo corregimos manualmente)
        if '__pycache__' in file_path or '.git' in file_path or file_path.endswith('main.py'):
            continue
            
        total_count += 1
        if add_hybrid_imports(file_path):
            fixed_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos procesados: {total_count}")
    print(f"   - Archivos corregidos: {fixed_count}")
    print(f"   - Archivos sin cambios: {total_count - fixed_count}")

if __name__ == "__main__":
    main()
