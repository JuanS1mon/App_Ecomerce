#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de HTML para el sistema multi-tabla
Crea formularios Bootstrap 5 responsivos y funcionales
"""

import sys
import os
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent))

async def generar_formularios_html_biblioteca():
    """Generar formularios HTML para el sistema de biblioteca"""
    print("🌐 GENERANDO FORMULARIOS HTML")
    print("=" * 50)
    
    try:
        from routers.config.generator_config import (
            MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig
        )
        from routers.config.nuevo_generador_multi_tabla import generar_estructura_completa_por_tabla
        from routers.config.Generar import generate_dynamic_html_forms
        
        # Configuración de ejemplo
        config_data = {
            "service_name": "biblioteca_sistema",
            "description": "Sistema completo de gestión de biblioteca",
            "tables": [
                {
                    "name": "autores",
                    "description": "Gestión de autores",
                    "fields": [
                        {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True, "nullable": False},
                        {"name": "nombre", "field_type": "string", "max_length": 100, "nullable": False, "description": "Nombre del autor"},
                        {"name": "email", "field_type": "email", "max_length": 150, "nullable": True, "description": "Email del autor"},
                        {"name": "fecha_nacimiento", "field_type": "date", "nullable": True, "description": "Fecha de nacimiento"}
                    ]
                },
                {
                    "name": "libros",
                    "description": "Catálogo de libros",
                    "fields": [
                        {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True, "nullable": False},
                        {"name": "titulo", "field_type": "string", "max_length": 200, "nullable": False, "description": "Título del libro"},
                        {"name": "isbn", "field_type": "string", "max_length": 20, "unique": True, "nullable": False, "description": "ISBN del libro"},
                        {"name": "autor_id", "field_type": "integer", "foreign_key": "autores.id", "nullable": False, "description": "Autor del libro"},
                        {"name": "disponible", "field_type": "boolean", "nullable": False, "default_value": "true", "description": "Disponibilidad"}
                    ]
                }
            ],
            "relationships": [
                {
                    "relationship_type": "one_to_many",
                    "from_table": "autores",
                    "from_field": "id",
                    "to_table": "libros",
                    "to_field": "autor_id",
                    "relationship_name": "libros",
                    "back_populates": "autor"
                }
            ]
        }
        
        # Crear objetos de configuración
        tables = []
        for table_data in config_data['tables']:
            fields = []
            for field_data in table_data['fields']:
                field = FieldConfig(**field_data)
                fields.append(field)
            
            table = TableConfig(
                name=table_data['name'],
                fields=fields,
                description=table_data.get('description')
            )
            tables.append(table)
        
        relationships = []
        for rel_data in config_data['relationships']:
            relationship = RelationshipConfig(**rel_data)
            relationships.append(relationship)
        
        service_config = MultiTableServiceConfig(
            service_name=config_data['service_name'],
            description=config_data['description'],
            tables=tables,
            relationships=relationships
        )
        
        print(f"📋 Generando HTML para: {service_config.service_name}")
        
        # Generar HTML
        html_result = await generate_dynamic_html_forms(service_config)
        
        if html_result["success"]:
            print("🎉 ¡Formularios HTML generados exitosamente!")
            print(f"📁 Archivos HTML: {html_result['forms_count']}")
            
            for form_file_path in html_result['generated_forms']:
                file_name = Path(form_file_path).name
                print(f"   ✅ {file_name}")
                
                # Verificar que existe
                if Path(form_file_path).exists():
                    print(f"      📊 Tamaño: {Path(form_file_path).stat().st_size} bytes")
                else:
                    print(f"      ❌ Archivo no encontrado")
            
            return True
        else:
            print("❌ Error generando HTML:")
            print(f"   {html_result.get('error', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_urls_acceso():
    """Mostrar URLs para acceder a los formularios"""
    print("\n🌐 URLS DE ACCESO A LOS FORMULARIOS")
    print("=" * 50)
    print("Una vez que el servidor esté ejecutándose:")
    print()
    print("🏠 Página principal:")
    print("   http://localhost:8000/static/html/forms/biblioteca_sistema/index.html")
    print()
    print("👥 Gestión de Autores:")
    print("   http://localhost:8000/static/html/forms/biblioteca_sistema/autores_form.html")
    print()
    print("📚 Gestión de Libros:")
    print("   http://localhost:8000/static/html/forms/biblioteca_sistema/libros_form.html")
    print()
    print("📊 APIs REST disponibles:")
    print("   • GET  http://localhost:8000/biblioteca_sistema/autores/")
    print("   • POST http://localhost:8000/biblioteca_sistema/autores/")
    print("   • GET  http://localhost:8000/biblioteca_sistema/libros/")
    print("   • POST http://localhost:8000/biblioteca_sistema/libros/")

async def main():
    """Función principal"""
    success = await generar_formularios_html_biblioteca()
    
    if success:
        mostrar_urls_acceso()
        print("\n💡 Para probar el sistema completo:")
        print("   1. Ejecuta: uvicorn sql_app.main:app --reload")
        print("   2. Registra las rutas en main.py:")
        print("      from Services.biblioteca_sistema.route_config_biblioteca_sistema import configure_biblioteca_sistema_routes")
        print("      configure_biblioteca_sistema_routes(app)")
        print("   3. Accede a los formularios usando las URLs de arriba")
    else:
        print("\n❌ Error generando formularios HTML")

if __name__ == "__main__":
    asyncio.run(main())