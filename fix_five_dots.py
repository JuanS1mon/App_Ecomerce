#!/usr/bin/env python3
import os
import re

def fix_five_dot_imports():
    """
    Corrige importaciones con .....db por ....db en archivos de Services
    """
    services_dir = r"c:\Users\PCJuan\Desktop\sql_app\sql_app\Services"
    files_fixed = 0
    
    # Buscar todos los archivos .py en Services
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Reemplazar importaciones con 5 puntos por 4 puntos
                    content = re.sub(r'from \.\.\.\.\.db', 'from ....db', content)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"✅ Corregido: {file_path}")
                        files_fixed += 1
                    
                except Exception as e:
                    print(f"❌ Error en {file_path}: {e}")
    
    print(f"\n🎉 Total de archivos corregidos: {files_fixed}")
    return files_fixed

if __name__ == "__main__":
    print("🔧 Corrigiendo importaciones con 5 puntos en Services...")
    fix_five_dot_imports()
