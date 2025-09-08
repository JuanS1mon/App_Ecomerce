# ============================================================================
# GENERAR.PY - GENERADOR DE CÓDIGO MEJORADO (VERSIÓN LIMPIA)
# ============================================================================
"""
Generador automático de código para aplicaciones FastAPI.
Sistema refactorizado con arquitectura mejorada, validaciones robustas y logging unificado.
Versión simplificada sin funcionalidades de Fase 2.
"""

from starlette.responses import FileResponse
import logging
import os
import time
from typing import Dict, Any, List

from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import fileinput
import traceback

# Importar el nuevo sistema de generación
from .generator_config import (
    GENERATOR_CONFIG, VALIDATOR, PATH_MANAGER, MULTI_TABLE_VALIDATOR,
    MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig
)
from .generator_logger import main_logger, GenerationSession, error_handler
from .generator_factory import generator_factory
from .multi_table_generator import multi_table_factory, MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig

templates = Jinja2Templates(directory="sql_app/static")

# Logger principal del módulo
logger = main_logger

router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
    prefix="/generar",
    tags=["generar"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/")
async def migraciones_page(request: Request):
    """Endpoint principal del generador (sin autenticación para facilidad de uso)"""
    try:
        logger.log_user_action("Acceso a página principal del generador")
        
        # Crear datos de usuario básicos para compatibilidad
        mock_user_data = {
            "user": {"username": "generator_user", "email": "generator@example.com"},
            "user_count": 1,
            "activities": [],
            "is_admin": True,
            "is_authenticated": True
        }
        
        # Verificar si el archivo existe
        template_path = "sql_app/static/html/generar.html"
        if os.path.exists(template_path):
            logger.log_template_render("generar.html", True)
            
            return templates.TemplateResponse("html/generar.html", {
                "request": request, 
                **mock_user_data
            })
        else:
            logger.log_template_render("generar.html", False)
            logger.error(f"❌ Template file not found: {template_path}")
            
            return HTMLResponse(content="""
            <html>
                <head><title>Generador de Aplicaciones</title></head>
                <body>
                    <h1>🛠️ Generador de Aplicaciones</h1>
                    <p>El archivo generar.html no se encontró en la ruta esperada.</p>
                    <p>Ruta buscada: sql_app/static/html/generar.html</p>
                    <p><a href="/login">Ir al login</a></p>
                </body>
            </html>
            """, status_code=200)
            
    except Exception as e:
        logger.log_generation_error(e, "renderizado de template principal")
        
        # Fallback a una respuesta simple en caso de error
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=f"""
        <html>
            <head><title>Error Temporal</title></head>
            <body>
                <h1>Generador de Aplicaciones</h1>
                <p>Error temporal al cargar la página. Por favor, inténtelo de nuevo.</p>
                <p>Error: {str(e)}</p>
                <p><a href="/login">Ir al login</a></p>
            </body>
        </html>
        """, status_code=200)

@router.post("/generate")
async def generate(request: Request):
    """Endpoint principal para la generación de código"""
    start_time = time.time()

    try:
        # Obtener datos del JSON
        json_data = await request.json()
        module_name = json_data["module_name"]
        field_names = json_data.get("field_names", [])
        field_types = json_data.get("field_types", [])

        # Procesar opciones elegidas por el usuario
        options = {
            'generate_crud': json_data.get('generate_crud', False),
            'generate_route': json_data.get('generate_route', False),
            'generate_schema': json_data.get('generate_schema', False),
            'generate_html_form': json_data.get('generate_html_form', False),
            'generate_tests': json_data.get('generate_tests', False),
            'agregar_rutas': json_data.get('agregar_rutas', False),
            'generate_service': json_data.get('generate_service', False)
        }

        logger.log_user_action(f"Solicitud de generación - Módulo: {module_name}")
        logger.log_debug_info("Opciones de generación", options)

        # Validar datos de entrada
        try:
            VALIDATOR.validate_all(module_name, field_names, field_types, options)
        except ValueError as e:
            return {"success": False, "message": str(e)}

        # Determinar tipo de generación
        if options['generate_service']:
            return await generate_complete_service(module_name, field_names, field_types)
        else:
            return await generate_individual_components(module_name, field_names, field_types, options)

    except Exception as e:
        logger.log_generation_error(e, "endpoint principal")
        return {"success": False, "message": f"Error interno: {str(e)}"}
    finally:
        duration = time.time() - start_time
        logger.log_performance("Endpoint generate", duration)

@router.post("/generate-multi-table")
async def generate_multi_table(request: Request):
    """Endpoint para generación de servicios multi-tabla"""
    import sys
    start_time = time.time()
    
    try:
        print("🌐 === ENDPOINT /generate-multi-table RECIBIDO ===", flush=True)
        sys.stdout.flush()
        
        # Obtener JSON del request
        print("🔍 Obteniendo JSON del request...", flush=True)
        sys.stdout.flush()
        json_data = await request.json()
        print(f"✅ JSON recibido: {json_data.get('service_name', 'sin nombre')}", flush=True)
        sys.stdout.flush()
        
        logger.log_user_action(f"Solicitud de generación multi-tabla - Servicio: {json_data.get('service_name', 'no especificado')}")
        logger.log_debug_info("Configuración multi-tabla", json_data)
        
        # Validar estructura JSON básica
        print("🔍 Validando estructura JSON...", flush=True)
        sys.stdout.flush()
        validation_errors = MULTI_TABLE_VALIDATOR.validate_json_structure(json_data)
        if validation_errors:
            print(f"❌ Errores de validación JSON: {validation_errors}", flush=True)
            sys.stdout.flush()
            return {"success": False, "message": "Errores en JSON", "errors": validation_errors}
        print("✅ Estructura JSON válida", flush=True)
        sys.stdout.flush()
        
        # Convertir JSON a configuración
        try:
            print("🔍 Convirtiendo JSON a configuración...", flush=True)
            sys.stdout.flush()
            service_config = create_service_config_from_json(json_data)
            print("✅ Configuración creada exitosamente", flush=True)
            
            # AUTO-CORRECCIÓN DE RELACIONES
            print("🔧 Iniciando auto-corrección de relaciones...", flush=True)
            service_config = auto_fix_relationships(service_config)
            print("✅ Relaciones auto-corregidas", flush=True)
            sys.stdout.flush()
        except Exception as e:
            error_msg = f"❌ Error al procesar configuración: {str(e)}"
            print(error_msg, flush=True)
            sys.stdout.flush()
            return {"success": False, "message": error_msg}
        
        # Validar configuración completa
        print("🔍 Validando configuración completa...", flush=True)
        sys.stdout.flush()
        
        # DEBUG: Mostrar estructura de tablas y relaciones
        print("🔍 DEBUG - Estructura de tablas:", flush=True)
        for table in service_config.tables:
            field_names = [field.name for field in table.fields]
            print(f"  📋 Tabla '{table.name}': campos = {field_names}", flush=True)
        
        print("🔍 DEBUG - Relaciones configuradas:", flush=True)
        for rel in service_config.relationships:
            print(f"  🔗 {rel.from_table}.{rel.from_field} -> {rel.to_table}.{rel.to_field}", flush=True)
        sys.stdout.flush()
        
        config_errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        if config_errors:
            print(f"❌ Errores de configuración: {config_errors}", flush=True)
            sys.stdout.flush()
            return {"success": False, "message": "Errores en configuración", "errors": config_errors}
        print("✅ Configuración válida", flush=True)
        sys.stdout.flush()
        
        # Generar el servicio multi-tabla
        print("🚀 Llamando a generate_multi_table_service...", flush=True)
        sys.stdout.flush()
        result = await generate_multi_table_service(service_config)
        print(f"✅ Resultado de generación: {result}", flush=True)
        sys.stdout.flush()
        
        return result
            
    except Exception as e:
        error_msg = f"❌ ERROR EN ENDPOINT: {str(e)}"
        print(error_msg, flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        logger.log_generation_error(e, "endpoint multi-tabla")
        return {"success": False, "message": f"Error interno: {str(e)}"}
    finally:
        duration = time.time() - start_time
        print(f"⏱️ Duración total del endpoint: {duration:.3f}s", flush=True)
        sys.stdout.flush()
        logger.log_performance("Endpoint generate-multi-table", duration)

@router.get("/multi-table-example")
async def get_multi_table_example():
    """Endpoint que devuelve un ejemplo de JSON para configuración multi-tabla"""
    
    example_config = {
        "service_name": "biblioteca_sistema",
        "description": "Sistema básico de gestión de biblioteca con autores y libros",
        "tables": [
            {
                "name": "autores",
                "description": "Tabla de autores",
                "fields": [
                    {
                        "name": "id",
                        "field_type": "integer",
                        "primary_key": True,
                        "auto_increment": True,
                        "nullable": False
                    },
                    {
                        "name": "nombre",
                        "field_type": "string",
                        "max_length": 100,
                        "nullable": False
                    },
                    {
                        "name": "email",
                        "field_type": "string",
                        "max_length": 150,
                        "unique": True
                    },
                    {
                        "name": "fecha_creacion",
                        "field_type": "datetime",
                        "default_value": "now()"
                    }
                ]
            },
            {
                "name": "libros",
                "description": "Tabla de libros",
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
                        "max_length": 200,
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
                        "name": "fecha_publicacion",
                        "field_type": "date"
                    },
                    {
                        "name": "precio",
                        "field_type": "decimal"
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
            }
        ],
        "generate_crud_for_all": True,
        "generate_relationship_endpoints": True
    }
    
    return {
        "success": True,
        "example": example_config,
        "description": "Ejemplo de configuración JSON para sistema multi-tabla",
        "instructions": [
            "1. Copia este JSON y modifícalo según tus necesidades",
            "2. Envía el JSON modificado al endpoint POST /generar/generate-multi-table",
            "3. El sistema generará automáticamente todos los modelos y CRUDs relacionados"
        ]
    }

async def generate_complete_service(module_name: str, field_names: List[str], field_types: List[str]) -> Dict[str, Any]:
    """Generar un servicio completo y su archivo de configuración de rutas"""
    try:
        service_generator = generator_factory.create_generator('service')
        result = service_generator.generate_service_components(module_name, field_names, field_types)

        if result["success"]:
            message = f"✅ Servicio '{module_name}' generado exitosamente"
            if result["generated_files"]:
                message += f"\n📁 Archivos generados: {len(result['generated_files'])}"
            if result["errors"]:
                message += f"\n⚠️ Errores encontrados: {len(result['errors'])}"

            # Crear archivo de configuración de rutas
            route_config_filename = f"route_config_{module_name}.py"
            route_config_path = os.path.join("sql_app", "routers", route_config_filename)
            try:
                with open(route_config_path, "w") as route_file:
                    route_file.write(f"""# Archivo de configuración de rutas para el módulo {module_name}\n\n""")
                    route_file.write(f"from fastapi import APIRouter\n")
                    route_file.write(f"from .{module_name} import router as {module_name}_router\n\n")
                    route_file.write(f"router = APIRouter()\n")
                    route_file.write(f"router.include_router({module_name}_router, prefix='/{module_name}', tags=['{module_name}'])\n")
                result["generated_files"].append(route_config_path)
                message += f"\n📁 Archivo de configuración de rutas generado: {route_config_filename}"
            except Exception as e:
                logger.error(f"Error al crear el archivo de configuración de rutas: {str(e)}")
                result["errors"].append(f"Error al crear archivo de configuración de rutas: {str(e)}")

            return {"success": True, "message": message, "details": result}
        else:
            return {"success": False, "message": f"❌ Error generando servicio '{module_name}'", "details": result}

    except Exception as e:
        return error_handler.handle_generation_error(e, "servicio", module_name)

async def generate_individual_components(module_name: str, field_names: List[str], 
                                       field_types: List[str], options: Dict[str, bool]) -> Dict[str, Any]:
    """Generar componentes individuales según las opciones seleccionadas"""
    results = {"success": True, "generated_files": [], "errors": []}
    
    with GenerationSession(module_name, "componentes individuales", logger) as session:
        
        # Mapeo de opciones a generadores
        component_map = {
            'generate_crud': 'crud',
            'generate_route': 'route', 
            'generate_schema': 'schema',
            'generate_html_form': 'html',
            'generate_tests': 'test'
        }
        
        for option, generator_type in component_map.items():
            if options.get(option, False):
                try:
                    generator = generator_factory.create_generator(generator_type)
                    result = generator.generate_and_save(module_name, field_names, field_types)
                    
                    if result["success"]:
                        session.add_generated_file(result["file_path"])
                        results["generated_files"].append(result["file_path"])
                    else:
                        session.add_error(Exception(result.get("message", "Error desconocido")), generator_type)
                        results["errors"].append(result.get("message", f"Error en {generator_type}"))
                        
                except Exception as e:
                    session.add_error(e, generator_type)
                    results["errors"].append(f"Error en {generator_type}: {str(e)}")
        
        # Agregar rutas al main.py si está habilitado
        if options.get('agregar_rutas', False) and options.get('generate_route', False):
            try:
                add_new_route_to_main(module_name)
                session.add_generated_file("main.py (actualizado)")
            except Exception as e:
                session.add_error(e, "agregar rutas a main.py")
                results["errors"].append(f"Error agregando rutas: {str(e)}")
        
        # Determinar resultado final
        if results["errors"]:
            results["success"] = len(results["generated_files"]) > 0
        
        # Preparar mensaje de respuesta
        if results["success"]:
            message = f"✅ Generación completada - {len(results['generated_files'])} archivos creados"
            if results["errors"]:
                message += f" (con {len(results['errors'])} errores)"
        else:
            message = f"❌ Error en la generación - {len(results['errors'])} errores encontrados"
    
    return {"success": results["success"], "message": message, "details": results}

def create_service_config_from_json(json_data: dict) -> MultiTableServiceConfig:
    """Convertir JSON a configuración de servicio multi-tabla"""
    
    # Crear configuraciones de tabla
    tables = []
    for table_data in json_data.get('tables', []):
        # Crear configuraciones de campo
        fields = []
        for field_data in table_data.get('fields', []):
            field_config = FieldConfig(
                name=field_data['name'],
                field_type=field_data['field_type'],
                max_length=field_data.get('max_length'),
                nullable=field_data.get('nullable', True),
                unique=field_data.get('unique', False),
                primary_key=field_data.get('primary_key', False),
                auto_increment=field_data.get('auto_increment', False),
                default_value=field_data.get('default_value'),
                foreign_key=field_data.get('foreign_key'),
                index=field_data.get('index', False)
            )
            fields.append(field_config)
        
        # Crear configuración de tabla
        table_config = TableConfig(
            name=table_data['name'],
            fields=fields,
            description=table_data.get('description')
        )
        tables.append(table_config)
    
    # Crear configuraciones de relación
    relationships = []
    for rel_data in json_data.get('relationships', []):
        rel_config = RelationshipConfig(
            relationship_type=rel_data['relationship_type'],
            from_table=rel_data['from_table'],
            from_field=rel_data['from_field'],
            to_table=rel_data['to_table'],
            to_field=rel_data['to_field'],
            relationship_name=rel_data['relationship_name'],
            back_populates=rel_data.get('back_populates'),
            cascade_delete=rel_data.get('cascade_delete', False),
            lazy_loading=rel_data.get('lazy_loading', 'select')
        )
        relationships.append(rel_config)
    
    # Crear configuración del servicio
    service_config = MultiTableServiceConfig(
        service_name=json_data['service_name'],
        description=json_data['description'],
        tables=tables,
        relationships=relationships,
        generate_crud_for_all=json_data.get('generate_crud_for_all', True),
        generate_relationship_endpoints=json_data.get('generate_relationship_endpoints', True)
    )
    
    return service_config

def auto_fix_relationships(service_config: MultiTableServiceConfig) -> MultiTableServiceConfig:
    """Auto-corregir relaciones incorrectas en la configuración"""
    import sys
    print("🔧 === INICIANDO AUTO-CORRECCIÓN DE RELACIONES ===", flush=True)
    
    # Crear un mapa de tablas para fácil acceso
    tables_map = {table.name: table for table in service_config.tables}
    
    # Lista de relaciones corregidas
    fixed_relationships = []
    
    for rel in service_config.relationships:
        print(f"🔍 Analizando relación: {rel.from_table}.{rel.from_field} -> {rel.to_table}.{rel.to_field}", flush=True)
        
        from_table = tables_map.get(rel.from_table)
        to_table = tables_map.get(rel.to_table)
        
        if not from_table or not to_table:
            print(f"⚠️ Saltando relación - tabla no encontrada", flush=True)
            continue
            
        # Verificar si el campo origen existe
        from_field_exists = any(f.name == rel.from_field for f in from_table.fields)
        
        if not from_field_exists:
            print(f"🔧 CORRIGIENDO: Campo '{rel.from_field}' no existe en '{rel.from_table}'", flush=True)
            
            # Estrategia de corrección basada en nombres
            if rel.relationship_type in ["one-to-many", "one_to_many"]:
                # Cambiar a many-to-one e invertir la relación
                new_from_field = f"{rel.from_table.replace('_1092', '')}_id"
                
                # Agregar el campo foreign key a la tabla destino
                foreign_key_field = FieldConfig(
                    name=new_from_field,
                    field_type="integer",
                    nullable=True,
                    foreign_key=f"{rel.from_table}.{rel.to_field}"
                )
                
                # Verificar si el campo ya existe
                field_exists = any(f.name == new_from_field for f in to_table.fields)
                if not field_exists:
                    print(f"➕ Agregando campo FK: {rel.to_table}.{new_from_field}", flush=True)
                    to_table.fields.append(foreign_key_field)
                
                # Crear relación corregida (many-to-one)
                fixed_rel = RelationshipConfig(
                    from_table=rel.to_table,
                    from_field=new_from_field,
                    to_table=rel.from_table,
                    to_field=rel.to_field,
                    relationship_type="many-to-one",
                    relationship_name=f"{rel.to_table}_to_{rel.from_table}",
                    back_populates=rel.back_populates,
                    cascade_delete=rel.cascade_delete,
                    lazy_loading=rel.lazy_loading
                )
                
                print(f"✅ Relación corregida: {fixed_rel.from_table}.{fixed_rel.from_field} -> {fixed_rel.to_table}.{fixed_rel.to_field}", flush=True)
                fixed_relationships.append(fixed_rel)
            else:
                # Para otras relaciones, mantener como está pero saltarla
                print(f"⚠️ Relación no auto-corregible: {rel.relationship_type}", flush=True)
        else:
            # La relación está bien, mantenerla
            print(f"✅ Relación válida, manteniéndola", flush=True)
            fixed_relationships.append(rel)
    
    # Actualizar las relaciones en el service_config
    service_config.relationships = fixed_relationships
    
    print(f"🎯 AUTO-CORRECCIÓN COMPLETADA: {len(fixed_relationships)} relaciones válidas", flush=True)
    sys.stdout.flush()
    
    return service_config

async def generate_multi_table_service(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Generar servicio completo multi-tabla usando el NUEVO GENERADOR"""
    import sys
    try:
        print(f"📊 === INICIO GENERACIÓN MULTI-TABLA ===", flush=True)
        sys.stdout.flush()
        
        # PASO 1: Verificar que la función se puede importar
        try:
            print("🔍 PASO 1: Intentando importar función...", flush=True)
            sys.stdout.flush()
            from .nuevo_generador_multi_tabla import generar_estructura_completa_por_tabla
            print("✅ PASO 1: Importación exitosa", flush=True)
            sys.stdout.flush()
        except Exception as import_error:
            error_msg = f"❌ PASO 1 FALLÓ: Error al importar: {import_error}"
            print(error_msg, flush=True)
            sys.stdout.flush()
            return {"success": False, "message": error_msg}
        
        # PASO 2: Verificar datos de entrada
        try:
            print("🔍 PASO 2: Verificando datos de entrada...", flush=True)
            print(f"✅ PASO 2: service_name = '{service_config.service_name}'", flush=True)
            print(f"✅ PASO 2: tablas = {len(service_config.tables)}", flush=True)
            print(f"✅ PASO 2: relaciones = {len(service_config.relationships)}", flush=True)
            sys.stdout.flush()
        except Exception as data_error:
            error_msg = f"❌ PASO 2 FALLÓ: Error en datos: {data_error}"
            print(error_msg, flush=True)
            sys.stdout.flush()
            return {"success": False, "message": error_msg}
        
        # PASO 3: Intentar ejecutar la función
        try:
            print("🚀 PASO 3: Ejecutando función generar_estructura_completa_por_tabla...", flush=True)
            sys.stdout.flush()
            
            result = generar_estructura_completa_por_tabla(service_config)
            
            print(f"✅ PASO 3: Función ejecutada. Resultado: {result}", flush=True)
            sys.stdout.flush()
            
            if result.get('success', False):
                files_count = len(result.get('generated_files', []))
                print(f"✅ Multi-tabla generado exitosamente: {files_count} archivos", flush=True)
                sys.stdout.flush()
                return {
                    "success": True,
                    "message": f"🎯 NUEVO GENERADOR: Servicio multi-tabla '{service_config.service_name}' generado exitosamente",
                    "generated_files": result.get('generated_files', []),
                    "files_count": files_count,
                    "service_config": {
                        "name": service_config.service_name,
                        "tables_count": len(service_config.tables),
                        "relationships_count": len(service_config.relationships)
                    }
                }
            else:
                error_msg = result.get('error', 'Error desconocido en la generación')
                print(f"❌ Error generando multi-tabla: {error_msg}", flush=True)
                sys.stdout.flush()
                return {"success": False, "message": f"Error al generar servicio multi-tabla: {error_msg}"}
                
        except Exception as exec_error:
            error_msg = f"❌ PASO 3 FALLÓ: Error ejecutando función: {exec_error}"
            print(error_msg, flush=True)
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            return {"success": False, "message": error_msg}
            
    except Exception as e:
        error_msg = f"❌ ERROR GENERAL: {str(e)}"
        print(error_msg, flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        return {"success": False, "message": error_msg}

def add_new_route_to_main(new_route):
    """Agregar nueva ruta al archivo main.py"""
    try:
        with fileinput.FileInput('main.py', inplace=False) as file:
            lines = list(file)
        last_maestros_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith('from routers.Maestros import'):
                if f'Route_{new_route}' not in line:
                    lines[i] = line.strip() + f', Route_{new_route}\n'
            if '#Maestros' in line:
                last_maestros_index = i
        if last_maestros_index is not None:
            lines.insert(last_maestros_index + 1, f'app.include_router(Route_{new_route}.router)\n')
        with open('main.py', 'w') as file:
            file.writelines(lines)
        
        logger.log_file_operation("actualización de rutas en main.py", "main.py", True)
        return True
    except Exception as e:
        logger.log_file_operation("actualización de rutas en main.py", "main.py", False)
        logger.log_generation_error(e, "agregar rutas a main.py")
        return False
