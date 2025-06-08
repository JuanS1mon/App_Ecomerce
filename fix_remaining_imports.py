#!/usr/bin/env python3
"""



Script para arreglar todas las importaciones relativas restantes
"""
import os
import re

def fix_imports_in_file(file_path):
    """Arregla las importaciones relativas en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de importaciones relativas a corregir
        patterns = [
            # Importaciones de 4 puntos
            (r'from \.\.\.\.db\.database import', 'from db.database import'),
            (r'from \.\.\.\.db\.models', 'from db.models'),
            (r'from \.\.\.\.db\.', 'from db.'),
            (r'from \.\.\.\.Services\.', 'from Services.'),
            (r'from \.\.\.\.routers\.', 'from routers.'),
            
            # Importaciones de 3 puntos
            (r'from \.\.\.db\.database import', 'from db.database import'),
            (r'from \.\.\.db\.models', 'from db.models'),
            (r'from \.\.\.db\.', 'from db.'),
            (r'from \.\.\.Services\.', 'from Services.'),
            (r'from \.\.\.routers\.', 'from routers.'),
            
            # Importaciones de 2 puntos
            (r'from \.\.db\.database import', 'from db.database import'),
            (r'from \.\.db\.models', 'from db.models'),
            (r'from \.\.db\.', 'from db.'),
            (r'from \.\.Services\.', 'from Services.'),
            (r'from \.\.routers\.', 'from routers.'),
            
            # Importaciones de 1 punto en contexto específico
            (r'from \.schema_', 'from Services.app_stock.articulos.schema_'),
            (r'from \.model_', 'from Services.app_stock.articulos.model_'),
            (r'from \.service_', 'from Services.app_stock.articulos.service_'),
            (r'from \.route_', 'from Services.app_stock.articulos.route_'),
        ]
        
        # Aplicar todas las correcciones
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Arreglado: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 Arreglando importaciones relativas restantes...")
    
    # Buscar archivos Python en Services
    services_dir = 'Services'
    fixed_count = 0
    
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    
    print(f"\n✅ Proceso completado. {fixed_count} archivos arreglados.")

if __name__ == "__main__":
    main()
