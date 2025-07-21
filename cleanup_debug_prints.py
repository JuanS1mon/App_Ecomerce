#!/usr/bin/env python3
"""
Script para limpiar prints de debug y optimizar para producción
Reemplaza print() statements con logger apropiados
"""

import os
import re
from pathlib import Path

def clean_debug_prints():
    """Limpia prints de debug en archivos de seguridad"""
    
    # Archivos a limpiar
    files_to_clean = [
        "sql_app/Services/security/security.py",
        "sql_app/Services/security/jwt_auth.py", 
        "sql_app/Services/security/roles_basicos.py",
        "sql_app/Services/tickets/route_ticket.py",
        "sql_app/Services/app_stock/stock/service_stock_calculado.py"
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            print(f"🧹 Limpiando {file_path}...")
            clean_file(file_path)
        else:
            print(f"⚠️  Archivo no encontrado: {file_path}")

def clean_file(file_path):
    """Limpia un archivo específico"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_lines = content.count('\n')
    
    # Patrones de prints de debug a remover o reemplazar
    patterns = [
        # Prints de diagnóstico completos
        (r'print\(f?"DIAGNÓSTICO.*?\)', 'logger.debug'),
        (r'print\("=+ DEBUGGING.*?".*?\)', '# Debug removido'),
        (r'print\(f?"Resultados SQL obtenidos:.*?\)', 'logger.debug'),
        
        # Prints informativos a convertir en logs
        (r'print\(f?"Rol.*?creado.*?\)', 'logger.info'),
        (r'print\(f?"Usuario.*?no encontrado.*?\)', 'logger.warning'),
        (r'print\(f?"Rol.*?asignado.*?\)', 'logger.info'),
        
        # Prints de debug específicos
        (r'print\(f?"Request received at:.*?\)', 'logger.debug'),
    ]
    
    modified_content = content
    changes_made = 0
    
    for pattern, replacement in patterns:
        if 'logger.' in replacement:
            # Reemplazar con logger apropiado
            matches = re.findall(pattern, modified_content, re.DOTALL)
            for match in matches:
                if 'DIAGNÓSTICO' in match:
                    # Solo en desarrollo
                    new_line = f'if ENVIRONMENT == "development": {replacement}({match[6:-1]})'
                else:
                    new_line = f'{replacement}({match[6:-1]})'
                
                modified_content = modified_content.replace(match, new_line)
                changes_made += 1
        else:
            # Comentar o remover
            modified_content = re.sub(pattern, f'# {replacement}', modified_content)
            changes_made += 1
    
    # Escribir archivo modificado
    if changes_made > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        final_lines = modified_content.count('\n')
        print(f"  ✅ {changes_made} cambios realizados")
        print(f"  📊 Líneas: {original_lines} -> {final_lines}")
    else:
        print(f"  ℹ️  No se requieren cambios")

if __name__ == "__main__":
    print("🚀 Iniciando limpieza de prints de debug...")
    clean_debug_prints()
    print("✨ Limpieza completada!")
