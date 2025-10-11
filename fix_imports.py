#!/usr/bin/env python3
"""
Script para corregir todos los imports que referencian sql_app.* incorrectamente
"""

import os
import re

def fix_imports_in_file(file_path):
    """Corrige los imports en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de imports a corregir
        replacements = [
            # from sql_app.config -> from config
            (r'from sql_app\.config import', 'from config import'),
            # from sql_app.db.database -> from db.database
            (r'from sql_app\.db\.database import', 'from db.database import'),
            # from db.models -> from db.models
            (r'from sql_app\.db\.models', 'from db.models'),
            # from db.schemas -> from db.schemas
            (r'from sql_app\.db\.schemas', 'from db.schemas'),
            # from routers -> from routers
            (r'from sql_app\.routers', 'from routers'),
            # from Services -> from Services
            (r'from sql_app\.Services', 'from Services'),
            # from middleware -> from middleware
            (r'from sql_app\.middleware', 'from middleware'),
            # from security -> from security
            (r'from sql_app\.security', 'from security'),
            # from utils -> from utils
            (r'from sql_app\.utils', 'from utils'),
            # from sql_app.logging_config -> from logging_config
            (r'from sql_app\.logging_config import', 'from logging_config import'),
            # from sql_app.app_settings -> from app_settings
            (r'from sql_app\.app_settings import', 'from app_settings import'),
            # from sql_app.exception_handlers -> from exception_handlers
            (r'from sql_app\.exception_handlers import', 'from exception_handlers import'),
            # from sql_app.init_app -> from init_app
            (r'from sql_app\.init_app import', 'from init_app import'),
            # from cache -> from cache
            (r'from sql_app\.cache', 'from cache'),
            # from monitoring -> from monitoring
            (r'from sql_app\.monitoring', 'from monitoring'),
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

def fix_all_imports():
    """Corrige imports en todos los archivos Python del proyecto"""
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
                if fix_imports_in_file(file_path):
                    files_changed += 1
                    print(f"✅ Corregido: {file_path}")
    
    print(f"\n🎉 Corrección completada! {files_changed} archivos modificados.")

if __name__ == "__main__":
    print("🔧 Iniciando corrección de imports...")
    fix_all_imports()