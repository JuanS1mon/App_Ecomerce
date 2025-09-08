#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de route_config
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append('.')

# Imports necesarios
from sql_app.routers.config.nuevo_generador_multi_tabla import generar_estructura_completa_por_tabla
from sql_app.routers.config.generator_config import MultiTableServiceConfig

def test_route_config():
    """Probar la generación de route_config"""
    
    # JSON de prueba simple
    test_json = {
        "service_name": "test_route_config",
        "description": "Test para verificar route_config",
        "tables": [
            {
                "name": "usuario_test",
                "description": "Usuario de prueba",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True},
                    {"name": "nombre", "field_type": "string", "primary_key": False, "auto_increment": False}
                ]
            },
            {
                "name": "producto_test", 
                "description": "Producto de prueba",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True},
                    {"name": "nombre", "field_type": "string", "primary_key": False, "auto_increment": False}
                ]
            }
        ],
        "relationships": []
    }
    
    try:
        # Crear configuración
        print("🔧 Creando configuración...")
        config = MultiTableServiceConfig(**test_json)
        
        # Generar
        print("🚀 Generando estructura...")
        result = generar_estructura_completa_por_tabla(config)
        
        print(f"✅ Resultado: {result['success']}")
        if result['success']:
            print(f"📁 Archivos generados: {len(result['generated_files'])}")
            for file in result['generated_files']:
                print(f"   - {file}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_route_config()
