#!/usr/bin/env python3
"""
Script para eliminar imports duplicados y estandarizar estructura
"""
import os
import re
from collections import defaultdict

def clean_duplicate_imports(file_path):
    """Limpia imports duplicados y estandariza la estructura"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Separar imports y resto del código
        import_lines = []
        code_lines = []
        in_imports = True
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('from ') or stripped.startswith('import '):
                if in_imports:
                    import_lines.append(line)
                else:
                    # Import en medio del código, mantener donde está
                    code_lines.append(line)
            elif stripped == '' and in_imports:
                import_lines.append(line)
            elif stripped.startswith('#') and in_imports and 'import' in stripped.lower():
                import_lines.append(line)
            else:
                if in_imports and stripped != '':
                    in_imports = False
                code_lines.append(line)
        
        # Procesar imports para eliminar duplicados
        stdlib_imports = set()
        third_party_imports = set()
        project_imports = set()
        
        for line in import_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # Categorizar imports
            if stripped.startswith('from sql_app') or stripped.startswith('from .') or stripped.startswith('from ..'):
                project_imports.add(stripped)
            elif any(lib in stripped for lib in ['fastapi', 'sqlalchemy', 'pydantic', 'jwt', 'bcrypt', 'passlib']):
                third_party_imports.add(stripped)
            else:
                stdlib_imports.add(stripped)
        
        # Generar nueva estructura de imports
        new_imports = []
        
        if stdlib_imports:
            new_imports.append("# Imports de bibliotecas estándar")
            for imp in sorted(stdlib_imports):
                new_imports.append(imp)
            new_imports.append("")
        
        if third_party_imports:
            new_imports.append("# Imports de terceros")
            for imp in sorted(third_party_imports):
                new_imports.append(imp)
            new_imports.append("")
        
        if project_imports:
            new_imports.append("# Imports del proyecto")
            for imp in sorted(project_imports):
                new_imports.append(imp)
            new_imports.append("")
        
        # Combinar todo
        new_content = '\n'.join(new_imports + code_lines)
        
        # Solo escribir si hay cambios
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    root_dir = r"c:\Users\PCJuan\Desktop\sql_app\sql_app"
    
    files_processed = 0
    files_changed = 0
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                files_processed += 1
                
                if clean_duplicate_imports(file_path):
                    files_changed += 1
                    print(f"✅ Limpiado: {file_path}")
                else:
                    print(f"⏭️  Sin cambios: {file_path}")
    
    print(f"\n📊 Resumen:")
    print(f"Archivos procesados: {files_processed}")
    print(f"Archivos modificados: {files_changed}")
    print("✅ Limpieza de imports completada")

if __name__ == "__main__":
    main()
