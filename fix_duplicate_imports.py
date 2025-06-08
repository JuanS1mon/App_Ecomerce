#!/usr/bin/env python3
"""
Script para eliminar imports duplicados y estandarizar la estructura de imports
en todo el proyecto FastAPI.
"""

import os
import re
from pathlib import Path

def get_python_files(directory):
    """Obtiene todos los archivos Python del directorio."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Excluir directorios específicos
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'env', '.venv', 'venv']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def clean_and_organize_imports(file_path):
    """Limpia y organiza los imports de un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo {file_path}: {e}")
        return False

    original_content = content
    lines = content.split('\n')
    
    # Categorías de imports
    standard_imports = set()
    third_party_imports = set()
    project_imports = set()
    
    # Imports encontrados para detectar duplicados
    found_imports = set()
    
    # Líneas que no son imports
    non_import_lines = []
    
    # Variables para rastrear el estado
    in_import_section = True
    first_non_import_found = False
    
    changes_made = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Si es una línea de import
        if stripped.startswith('from ') or stripped.startswith('import '):
            # Normalizar espacios múltiples
            normalized_import = re.sub(r'\s+', ' ', stripped)
            
            # Detectar imports duplicados
            if normalized_import in found_imports:
                print(f"🔄 Eliminando import duplicado en {file_path}: {normalized_import}")
                changes_made = True
                continue
            
            found_imports.add(normalized_import)
            
            # Categorizar imports
            if (normalized_import.startswith('from sql_app.') or 
                normalized_import.startswith('import sql_app') or
                normalized_import.startswith('from .') or
                normalized_import.startswith('from ...')):
                project_imports.add(normalized_import)
            elif any(lib in normalized_import for lib in ['fastapi', 'sqlalchemy', 'pydantic', 'uvicorn', 'jose', 'passlib', 'python-multipart']):
                third_party_imports.add(normalized_import)
            else:
                standard_imports.add(normalized_import)
                
            in_import_section = True
        else:
            # Si no es import y no es línea vacía o comentario al inicio
            if stripped and not stripped.startswith('#') and in_import_section:
                first_non_import_found = True
                in_import_section = False
            
            # Agregar línea si no estamos en la sección de imports inicial
            if first_non_import_found or not in_import_section:
                non_import_lines.append(line)
    
    # Detectar problemas específicos y corregirlos
    import_issues = []
    
    # Buscar imports problemáticos específicos
    problematic_patterns = [
        r'from sql_app\.db\.database import get_db.*import',  # imports concatenados
        r'from.*import.*get_db.*get_.*',  # múltiples imports en una línea
        r'from.*\).*\(',  # paréntesis mal cerrados
    ]
    
    for pattern in problematic_patterns:
        if re.search(pattern, original_content):
            changes_made = True
            import_issues.append(f"Patrón problemático encontrado: {pattern}")
    
    # Solo reconstruir si hay cambios
    if changes_made or len(found_imports) != len(set(found_imports)):
        # Reconstruir el archivo con imports organizados
        new_content_parts = []
        
        # Header del archivo (shebang, docstring, etc.)
        header_lines = []
        for line in lines:
            if line.strip().startswith('#') or line.strip() == '' or '"""' in line or "'''" in line:
                header_lines.append(line)
            else:
                break
        
        if header_lines:
            new_content_parts.extend(header_lines)
            new_content_parts.append('')
        
        # Imports de biblioteca estándar
        if standard_imports:
            new_content_parts.append('# Imports de bibliotecas estándar')
            for imp in sorted(standard_imports):
                new_content_parts.append(imp)
            new_content_parts.append('')
        
        # Imports de terceros
        if third_party_imports:
            new_content_parts.append('# Imports de terceros')
            for imp in sorted(third_party_imports):
                new_content_parts.append(imp)
            new_content_parts.append('')
        
        # Imports del proyecto
        if project_imports:
            new_content_parts.append('# Imports del proyecto')
            for imp in sorted(project_imports):
                new_content_parts.append(imp)
            new_content_parts.append('')
        
        # Resto del contenido
        new_content_parts.extend(non_import_lines)
        
        # Escribir archivo actualizado
        new_content = '\n'.join(new_content_parts)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Archivo actualizado: {file_path}")
            if import_issues:
                for issue in import_issues:
                    print(f"   🔧 {issue}")
            return True
            
        except Exception as e:
            print(f"❌ Error escribiendo {file_path}: {e}")
            return False
    
    return False

def main():
    """Función principal."""
    project_root = Path(__file__).parent / "sql_app"
    
    if not project_root.exists():
        print(f"❌ Directorio {project_root} no encontrado")
        return
    
    print(f"🔍 Buscando archivos Python en {project_root}")
    python_files = get_python_files(project_root)
    
    print(f"📁 Encontrados {len(python_files)} archivos Python")
    
    updated_files = 0
    
    for file_path in python_files:
        if clean_and_organize_imports(file_path):
            updated_files += 1
    
    print(f"\n📊 Resumen:")
    print(f"   Archivos procesados: {len(python_files)}")
    print(f"   Archivos actualizados: {updated_files}")
    print(f"   Archivos sin cambios: {len(python_files) - updated_files}")

if __name__ == "__main__":
    main()
