#!/usr/bin/env python3
"""
Script para corregir imports con 4 puntos específicamente
"""

import os
import re
import glob

def fix_four_dot_imports(file_path):
    """Corregir imports con cuatro puntos"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones específicos para 4 puntos
        patterns = [
            (r'from \.\.\.\.db\.', 'from db.'),
            (r'from \.\.\.\.Services\.', 'from Services.'),
            (r'from \.\.\.\.routers\.', 'from routers.'),
        ]
        
        # Aplicar correcciones
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Si el contenido cambió, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corregido: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 ARREGLANDO IMPORTS CON 4 PUNTOS")
    print("=" * 40)
    
    # Buscar archivos específicos con 4 puntos
    base_dir = r"c:\Users\PCJuan\Desktop\sql_app\sql_app"
    
    # Buscar todos los archivos Python
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Verificar si el archivo contiene imports con 4 puntos
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '....db.' in content or '....Services.' in content or '....routers.' in content:
                            python_files.append(file_path)
                except:
                    continue
    
    print(f"📁 Encontrados {len(python_files)} archivos con imports de 4 puntos")
    
    # Procesar cada archivo
    fixed_count = 0
    for file_path in python_files:
        if fix_four_dot_imports(file_path):
            fixed_count += 1
    
    print(f"\n✅ Proceso completado: {fixed_count} archivos corregidos")

if __name__ == "__main__":
    main()
