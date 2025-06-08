#!/usr/bin/env python3
"""
Script para corregir automáticamente todas las importaciones relativas problemáticas
en el proyecto sql_app
"""

import os
import re
import glob

def fix_imports_in_file(file_path, base_path):
    """Corrige las importaciones en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Calcular la ruta relativa desde el archivo actual hasta sql_app
        rel_path = os.path.relpath(file_path, base_path)
        dir_count = rel_path.count(os.sep) - 1  # -1 porque no contamos el archivo mismo
        
        # Generar los puntos necesarios para importaciones relativas
        dots = '.' * (dir_count + 1)
        
        # Patrones de importación que necesitan corrección
        patterns = [
            (r'^from db\.', f'from {dots}db.'),
            (r'^from Services\.', f'from {dots}Services.'),
            (r'^from routers\.', f'from {dots}routers.'),
        ]
        
        # Aplicar correcciones
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Solo escribir si hay cambios
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
    base_path = r"c:\Users\PCJuan\Desktop\sql_app\sql_app"
    
    if not os.path.exists(base_path):
        print(f"❌ No se encuentra el directorio base: {base_path}")
        return
    
    print("🔧 Iniciando corrección de importaciones...")
    
    # Buscar todos los archivos .py en sql_app
    pattern = os.path.join(base_path, "**", "*.py")
    python_files = glob.glob(pattern, recursive=True)
    
    fixed_count = 0
    total_count = 0
    
    for file_path in python_files:
        # Saltar archivos __pycache__ y similares
        if '__pycache__' in file_path or '.git' in file_path:
            continue
            
        total_count += 1
        if fix_imports_in_file(file_path, base_path):
            fixed_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos procesados: {total_count}")
    print(f"   - Archivos corregidos: {fixed_count}")
    print(f"   - Archivos sin cambios: {total_count - fixed_count}")
    
    if fixed_count > 0:
        print("\n✅ Correcciones completadas. Prueba ejecutar la aplicación nuevamente.")
    else:
        print("\n💡 No se encontraron archivos que necesiten corrección.")

if __name__ == "__main__":
    main()
