#!/usr/bin/env python3
"""
Script para arreglar todas las importaciones incorrectas específicas
"""
import os
import re

def fix_specific_imports_in_file(file_path):
    """Arregla importaciones específicas problemáticas"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Correcciones específicas
        specific_fixes = [
            # Articulos_tipos debe venir de su propio módulo
            (r'from Services\.app_stock\.articulos\.model_articulos_tipos import', 'from Services.app_stock.articulos_tipos.model_articulos_tipos import'),
            (r'from Services\.app_stock\.articulos\.schema_articulos_tipos import', 'from Services.app_stock.articulos_tipos.schema_articulos_tipos import'),
            (r'from Services\.app_stock\.articulos\.service_articulos_tipos import', 'from Services.app_stock.articulos_tipos.service_articulos_tipos import'),
            (r'from Services\.app_stock\.articulos\.route_articulos_tipos import', 'from Services.app_stock.articulos_tipos.route_articulos_tipos import'),
            
            # Articulos_series debe venir de su propio módulo
            (r'from Services\.app_stock\.articulos\.model_articulos_series import', 'from Services.app_stock.articulos_series.model_articulos_series import'),
            (r'from Services\.app_stock\.articulos\.schema_articulos_series import', 'from Services.app_stock.articulos_series.schema_articulos_series import'),
            (r'from Services\.app_stock\.articulos\.service_articulos_series import', 'from Services.app_stock.articulos_series.service_articulos_series import'),
            (r'from Services\.app_stock\.articulos\.route_articulos_series import', 'from Services.app_stock.articulos_series.route_articulos_series import'),
            
            # Stock debe venir de su propio módulo  
            (r'from Services\.app_stock\.articulos\.model_stock import', 'from Services.app_stock.stock.model_stock import'),
            (r'from Services\.app_stock\.articulos\.schema_stock import', 'from Services.app_stock.stock.schema_stock import'),
            (r'from Services\.app_stock\.articulos\.service_stock import', 'from Services.app_stock.stock.service_stock import'),
            (r'from Services\.app_stock\.articulos\.route_stock import', 'from Services.app_stock.stock.route_stock import'),
            
            # Depositos debe venir de su propio módulo
            (r'from Services\.app_stock\.articulos\.model_depositos import', 'from Services.app_stock.depositos.model_depositos import'),
            (r'from Services\.app_stock\.articulos\.schema_depositos import', 'from Services.app_stock.depositos.schema_depositos import'),
            (r'from Services\.app_stock\.articulos\.service_depositos import', 'from Services.app_stock.depositos.service_depositos import'),
            (r'from Services\.app_stock\.articulos\.route_depositos import', 'from Services.app_stock.depositos.route_depositos import'),
            
            # Depositos_tipos debe venir de su propio módulo
            (r'from Services\.app_stock\.articulos\.model_depositos_tipos import', 'from Services.app_stock.depositos_tipos.model_depositos_tipos import'),
            (r'from Services\.app_stock\.articulos\.schema_depositos_tipos import', 'from Services.app_stock.depositos_tipos.schema_depositos_tipos import'),
            (r'from Services\.app_stock\.articulos\.service_depositos_tipos import', 'from Services.app_stock.depositos_tipos.service_depositos_tipos import'),
            (r'from Services\.app_stock\.articulos\.route_depositos_tipos import', 'from Services.app_stock.depositos_tipos.route_depositos_tipos import'),
            
            # OT debe venir de su propio módulo
            (r'from Services\.app_stock\.articulos\.model_ot import', 'from Services.app_stock.ot.model_ot import'),
            (r'from Services\.app_stock\.articulos\.schema_ot import', 'from Services.app_stock.ot.schema_ot import'),
            (r'from Services\.app_stock\.articulos\.service_ot import', 'from Services.app_stock.ot.service_ot import'),
            (r'from Services\.app_stock\.articulos\.route_ot import', 'from Services.app_stock.ot.route_ot import'),
        ]
        
        # Aplicar todas las correcciones
        for pattern, replacement in specific_fixes:
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
    print("🔧 Arreglando importaciones específicas problemáticas...")
    
    # Buscar archivos Python en Services
    services_dir = 'Services'
    fixed_count = 0
    
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_specific_imports_in_file(file_path):
                    fixed_count += 1
    
    print(f"\n✅ Proceso completado. {fixed_count} archivos arreglados.")

if __name__ == "__main__":
    main()
