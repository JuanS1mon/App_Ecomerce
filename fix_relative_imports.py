#!/usr/bin/env python3
"""
Script para corregir todos los imports relativos (..) incorrectamente
"""

import os
import re

def fix_relative_imports_in_file(file_path):
    """Corrige los imports relativos en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de imports relativos a corregir
        replacements = [
            # from ..db.database -> from db.database
            (r'from \.\.db\.database import', 'from db.database import'),
            # from db.models -> from db.models
            (r'from \.\.db\.models', 'from db.models'),
            # from db.schemas -> from db.schemas
            (r'from \.\.db\.schemas', 'from db.schemas'),
            # from db.crud -> from db.crud
            (r'from \.\.db\.crud', 'from db.crud'),
            # from routers -> from routers
            (r'from \.\.routers', 'from routers'),
            # from Services -> from Services
            (r'from \.\.Services', 'from Services'),
            # from middleware -> from middleware
            (r'from \.\.middleware', 'from middleware'),
            # from security -> from security
            (r'from \.\.security', 'from security'),
            # from utils -> from utils
            (r'from \.\.utils', 'from utils'),
            # from ..config -> from config
            (r'from \.\.config import', 'from config import'),
            # from ..logging_config -> from logging_config
            (r'from \.\.logging_config import', 'from logging_config import'),
            # from ..app_settings -> from app_settings
            (r'from \.\.app_settings import', 'from app_settings import'),
            # from ..exception_handlers -> from exception_handlers
            (r'from \.\.exception_handlers import', 'from exception_handlers import'),
            # from ..init_app -> from init_app
            (r'from \.\.init_app import', 'from init_app import'),
        ]
        
        # Aplicar todas las correcciones
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def fix_all_relative_imports():
    """Corrige imports relativos en todos los archivos Python del proyecto"""
    files_changed = 0
    
    # Directorios a procesar
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for root, dirs, files in os.walk(base_dir):
        # Evitar directorios que no necesitamos
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.vscode', 'env', 'logs', 'backups']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_relative_imports_in_file(file_path):
                    files_changed += 1
                    print(f"✅ Corregido: {file_path}")
    
    print(f"\n🎉 Corrección de imports relativos completada! {files_changed} archivos modificados.")

if __name__ == "__main__":
    print("🔧 Iniciando corrección de imports relativos...")
    fix_all_relative_imports()