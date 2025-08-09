# ============================================================================
# DEMOSTRACIÓN COMPLETA DEL SISTEMA MULTI-TABLA (FASE 1)
# ============================================================================

import os
import sys
import json
import asyncio
import tempfile
import shutil
from pathlib import Path

# Agregar el path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sql_app.routers.config.generator_config import (
    MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig,
    MULTI_TABLE_VALIDATOR
)
from sql_app.routers.config.multi_table_generator import multi_table_factory
from sql_app.routers.config.Generar import create_service_config_from_json, generate_multi_table_service

async def demo_complete_workflow():
    """Demostración completa del flujo de trabajo multi-tabla"""
    
    print("=" * 70)
    print("🎬 DEMOSTRACIÓN COMPLETA: GENERADOR MULTI-TABLA (FASE 1)")
    print("=" * 70)
    print()

    # 1. Crear configuración JSON de ejemplo
    print("📋 Paso 1: Configuración JSON del sistema")
    print("-" * 40)
    
    biblioteca_json = {
        "service_name": "biblioteca_demo",
        "description": "Sistema completo de gestión de biblioteca",
        "tables": [
            {
                "name": "autores",
                "description": "Información de autores",
                "fields": [
                    {
                        "name": "id",
                        "field_type": "integer",
                        "primary_key": True,
                        "auto_increment": True,
                        "nullable": False
                    },
                    {
                        "name": "nombre_completo",
                        "field_type": "string",
                        "max_length": 150,
                        "nullable": False
                    },
                    {
                        "name": "email",
                        "field_type": "string",
                        "max_length": 100,
                        "unique": True
                    },
                    {
                        "name": "biografia",
                        "field_type": "text"
                    },
                    {
                        "name": "fecha_nacimiento",
                        "field_type": "date"
                    },
                    {
                        "name": "activo",
                        "field_type": "boolean",
                        "default_value": "true"
                    }
                ]
            },
            {
                "name": "libros",
                "description": "Catálogo de libros",
                "fields": [
                    {
                        "name": "id",
                        "field_type": "integer",
                        "primary_key": True,
                        "auto_increment": True,
                        "nullable": False
                    },
                    {
                        "name": "titulo",
                        "field_type": "string",
                        "max_length": 300,
                        "nullable": False
                    },
                    {
                        "name": "isbn",
                        "field_type": "string",
                        "max_length": 20,
                        "unique": True
                    },
                    {
                        "name": "autor_id",
                        "field_type": "integer",
                        "foreign_key": "autores.id",
                        "nullable": False
                    },
                    {
                        "name": "genero",
                        "field_type": "string",
                        "max_length": 50
                    },
                    {
                        "name": "fecha_publicacion",
                        "field_type": "date"
                    },
                    {
                        "name": "precio",
                        "field_type": "decimal"
                    },
                    {
                        "name": "stock",
                        "field_type": "integer",
                        "default_value": "0"
                    },
                    {
                        "name": "descripcion",
                        "field_type": "text"
                    }
                ]
            },
            {
                "name": "prestamos",
                "description": "Registro de préstamos",
                "fields": [
                    {
                        "name": "id",
                        "field_type": "integer",
                        "primary_key": True,
                        "auto_increment": True,
                        "nullable": False
                    },
                    {
                        "name": "libro_id",
                        "field_type": "integer",
                        "foreign_key": "libros.id",
                        "nullable": False
                    },
                    {
                        "name": "usuario_nombre",
                        "field_type": "string",
                        "max_length": 100,
                        "nullable": False
                    },
                    {
                        "name": "fecha_prestamo",
                        "field_type": "datetime",
                        "default_value": "now()"
                    },
                    {
                        "name": "fecha_devolucion",
                        "field_type": "datetime"
                    },
                    {
                        "name": "estado",
                        "field_type": "string",
                        "max_length": 20,
                        "default_value": "activo"
                    }
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
            },
            {
                "relationship_type": "one_to_many",
                "from_table": "libros",
                "from_field": "id",
                "to_table": "prestamos",
                "to_field": "libro_id",
                "relationship_name": "prestamos",
                "back_populates": "libro"
            }
        ],
        "generate_crud_for_all": True,
        "generate_relationship_endpoints": True
    }
    
    print(f"✅ Sistema configurado: {biblioteca_json['service_name']}")
    print(f"📊 Tablas definidas: {len(biblioteca_json['tables'])}")
    print(f"🔗 Relaciones: {len(biblioteca_json['relationships'])}")
    print()
    
    # 2. Validar JSON
    print("🔍 Paso 2: Validación de la configuración")
    print("-" * 40)
    
    try:
        service_config = create_service_config_from_json(biblioteca_json)
        validation_errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        
        if validation_errors:
            print("❌ Errores de validación encontrados:")
            for error in validation_errors:
                print(f"   • {error}")
            return False
        else:
            print("✅ Configuración válida")
            print(f"   • Servicio: {service_config.service_name}")
            print(f"   • Tablas: {len(service_config.tables)}")
            for table in service_config.tables:
                print(f"     - {table.name}: {len(table.fields)} campos")
            print(f"   • Relaciones: {len(service_config.relationships)}")
            for rel in service_config.relationships:
                print(f"     - {rel.from_table} → {rel.to_table} ({rel.relationship_type})")
    except Exception as e:
        print(f"❌ Error en validación: {str(e)}")
        return False
    
    print()
    
    # 3. Generar sistema completo
    print("⚙️ Paso 3: Generación del sistema multi-tabla")
    print("-" * 40)
    
    try:
        # Usar directorio temporal para la demostración
        temp_dir = tempfile.mkdtemp()
        print(f"📁 Directorio temporal: {temp_dir}")
        
        # Cambiar temporalmente la configuración
        from sql_app.routers.config.generator_config import GENERATOR_CONFIG
        original_services_path = GENERATOR_CONFIG.paths.services
        GENERATOR_CONFIG.paths.services = temp_dir
        
        try:
            # Generar el sistema
            result = await generate_multi_table_service(service_config)
            
            if result["success"]:
                print("✅ Generación exitosa")
                print(f"   📁 Archivos generados: {len(result['generated_files'])}")
                print(f"   📊 Tablas procesadas: {result['service_config']['tables_count']}")
                print(f"   🔗 Relaciones: {result['service_config']['relationships_count']}")
                print()
                
                # Mostrar archivos generados
                print("📄 Archivos creados:")
                for file_path in result['generated_files']:
                    relative_path = os.path.relpath(file_path, temp_dir)
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    print(f"   ✓ {relative_path} ({file_size:,} bytes)")
                print()
                
                # Mostrar contenido de ejemplo de un archivo generado
                models_file = None
                for file_path in result['generated_files']:
                    if 'models.py' in file_path:
                        models_file = file_path
                        break
                
                if models_file and os.path.exists(models_file):
                    print("🔍 Paso 4: Vista previa del código generado")
                    print("-" * 40)
                    print(f"📄 Archivo: {os.path.basename(models_file)}")
                    print()
                    
                    with open(models_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Mostrar primeras 50 líneas
                        lines = content.split('\n')[:50]
                        for i, line in enumerate(lines, 1):
                            print(f"{i:3d} | {line}")
                        
                        total_lines_count = len(content.split('\n'))
                        if total_lines_count > 50:
                            remaining_lines = total_lines_count - 50
                            print(f"... ({remaining_lines} líneas más)")
                    
                    print()
                
                # Mostrar estadísticas del código generado
                print("📊 Paso 5: Estadísticas del código generado")
                print("-" * 40)
                
                total_lines = 0
                total_size = 0
                file_types = {}
                
                for file_path in result['generated_files']:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            total_lines += lines
                        
                        size = os.path.getsize(file_path)
                        total_size += size
                        
                        ext = os.path.splitext(file_path)[1] or 'sin extensión'
                        file_types[ext] = file_types.get(ext, 0) + 1
                
                print(f"   📊 Total de líneas de código: {total_lines:,}")
                print(f"   💾 Tamaño total: {total_size:,} bytes")
                print(f"   📁 Tipos de archivo:")
                for ext, count in file_types.items():
                    print(f"      - {ext}: {count} archivo(s)")
                print()
                
                # Verificar funcionalidad específica
                print("🧪 Paso 6: Verificación de funcionalidades")
                print("-" * 40)
                
                checks = [
                    ("Modelos con relaciones", "relationship(" in content),
                    ("Foreign Keys", "ForeignKey(" in content),
                    ("Operaciones CRUD", any("CRUD" in fp for fp in result['generated_files'])),
                    ("Operaciones relacionadas", any("relations.py" in fp for fp in result['generated_files'])),
                    ("Métodos back_populates", "back_populates=" in content)
                ]
                
                for check_name, check_result in checks:
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}")
                
                print()
                print("🎉 ¡DEMOSTRACIÓN COMPLETADA EXITOSAMENTE!")
                print("=" * 70)
                print()
                print("📋 RESUMEN:")
                print(f"   • Sistema multi-tabla '{service_config.service_name}' generado")
                print(f"   • {len(service_config.tables)} tablas con {sum(len(t.fields) for t in service_config.tables)} campos total")
                print(f"   • {len(service_config.relationships)} relaciones configuradas")
                print(f"   • {len(result['generated_files'])} archivos de código creados")
                print(f"   • {total_lines:,} líneas de código generadas automáticamente")
                print()
                print("✅ La Fase 1 del sistema multi-tabla está completamente operativa")
                
            else:
                print("❌ Error en la generación:")
                print(f"   {result['message']}")
                if result.get('errors'):
                    for error in result['errors']:
                        print(f"   • {error}")
                return False
                
        finally:
            # Restaurar configuración original
            GENERATOR_CONFIG.paths.services = original_services_path
            
            # Mostrar archivos antes de limpiar (opcional)
            print(f"\n📁 Archivos generados en: {temp_dir}")
            print("   (Se limpiarán automáticamente)")
            
            # Limpiar directorio temporal
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        print(f"❌ Error en generación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def demo_api_endpoints():
    """Demostrar los endpoints de la API"""
    print("\n" + "=" * 70)
    print("🌐 DEMOSTRACIÓN DE ENDPOINTS API")
    print("=" * 70)
    
    print("📍 Endpoints disponibles en el servidor demo:")
    print("   • http://localhost:8001/")
    print("   • http://localhost:8001/generar/test (Interfaz visual)")
    print("   • http://localhost:8001/generar/multi-table-example (Ejemplo JSON)")
    print("   • POST http://localhost:8001/generar/generate-multi-table (Generación)")
    print()
    print("🧪 Para probar la interfaz completa:")
    print("   1. Abre http://localhost:8001/generar/test")
    print("   2. Haz clic en 'Sistema Multi-Tabla'")
    print("   3. Haz clic en 'Configurar con JSON'")
    print("   4. Usa 'Cargar Ejemplo' para obtener un JSON válido")
    print("   5. Haz clic en 'Generar Sistema'")

async def main():
    """Función principal de la demostración"""
    print("🚀 Iniciando demostración del sistema multi-tabla...")
    print()
    
    # Ejecutar demostración completa del workflow
    success = await demo_complete_workflow()
    
    if success:
        # Mostrar información de endpoints
        await demo_api_endpoints()
        
        print("\n" + "🎯 PRÓXIMOS PASOS PARA FASE 2:")
        print("   • Soporte para N tablas (3+)")
        print("   • Relaciones many-to-many")
        print("   • Editor visual drag & drop")
        print("   • Queries complejas con múltiples JOINs")
        print("   • Integración con IA para generación automática")
    else:
        print("\n❌ La demostración falló. Revisa los logs para más detalles.")

if __name__ == "__main__":
    asyncio.run(main())
