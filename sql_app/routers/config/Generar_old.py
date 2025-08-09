# ============================================================================
# GENERAR.PY - GENERADOR DE CÓDIGO MEJORADO
# ============================================================================
"""
Generador automático de código para aplicaciones FastAPI.
Sistema refactorizado con arquitectura mejorada, validaciones robustas y logging unificado.
"""

from starlette.responses import FileResponse
import logging
import os
import time
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import fileinput
import traceback

from sql_app.Services.security.auth_middleware import require_auth_for_template

# Importar el nuevo sistema de generación
from .generator_config import GENERATOR_CONFIG, VALIDATOR, PATH_MANAGER, MULTI_TABLE_VALIDATOR
from .generator_logger import main_logger, GenerationSession, error_handler
from .generator_factory import generator_factory
from .multi_table_generator import multi_table_factory, MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig

templates = Jinja2Templates(directory="sql_app/static")

# Logger principal del módulo
logger = main_logger

router = APIRouter(
    include_in_schema=False ,  # Oculta todas las rutas de este router en la documentación
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
        # Obtener datos del formulario
        form_data = await request.form()
        module_name = form_data["module_name"]
        field_names = form_data.getlist("field_names[]")
        field_types = form_data.getlist("field_types[]")

        # Procesar opciones elegidas por el usuario
        options = {
            'generate_crud': form_data.get('generate_crud') == 'true',
            'generate_route': form_data.get('generate_route') == 'true',
            'generate_schema': form_data.get('generate_schema') == 'true',
            'generate_html_form': form_data.get('generate_html_form') == 'true',
            'generate_tests': form_data.get('generate_tests') == 'true',
            'agregar_rutas': form_data.get('agregar_rutas') == 'true',
            'generate_service': form_data.get('generate_service') == 'true'
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
    """Endpoint para generación de servicios multi-tabla (FASE 1)"""
    start_time = time.time()
    
    try:
        # Obtener JSON del request
        json_data = await request.json()
        
        logger.log_user_action(f"Solicitud de generación multi-tabla - Servicio: {json_data.get('service_name', 'no especificado')}")
        logger.log_debug_info("Configuración multi-tabla", json_data)
        
        # Validar estructura JSON básica
        validation_errors = MULTI_TABLE_VALIDATOR.validate_json_structure(json_data)
        if validation_errors:
            return {"success": False, "message": "Errores en JSON", "errors": validation_errors}
        
        # Convertir JSON a configuración
        try:
            service_config = create_service_config_from_json(json_data)
        except Exception as e:
            return {"success": False, "message": f"Error al procesar configuración: {str(e)}"}
        
        # Validar configuración completa
        config_errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        if config_errors:
            return {"success": False, "message": "Errores en configuración", "errors": config_errors}
        
        # Generar el servicio multi-tabla
        result = await generate_multi_table_service(service_config)
        
        return result
            
    except Exception as e:
        logger.log_generation_error(e, "endpoint multi-tabla")
        return {"success": False, "message": f"Error interno: {str(e)}"}
    finally:
        duration = time.time() - start_time
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
    """Generar un servicio completo"""
    try:
        service_generator = generator_factory.create_generator('service')
        result = service_generator.generate_service_components(module_name, field_names, field_types)
        
        if result["success"]:
            message = f"✅ Servicio '{module_name}' generado exitosamente"
            if result["generated_files"]:
                message += f"\n📁 Archivos generados: {len(result['generated_files'])}"
            if result["errors"]:
                message += f"\n⚠️ Errores encontrados: {len(result['errors'])}"
            
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

async def generate_multi_table_service(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Generar servicio completo multi-tabla usando el NUEVO GENERADOR"""
    try:
        print(f"📊 Iniciando generación multi-tabla con NUEVO GENERADOR - Estructura individual por tabla")
        
        # Importar y usar el nuevo generador directamente
        from .nuevo_generador_multi_tabla import generar_estructura_completa_por_tabla
        
        # USAR EL NUEVO GENERADOR DIRECTAMENTE
        result = generar_estructura_completa_por_tabla(service_config)
        
        if result['success']:
            print(f"✅ Multi-tabla generado exitosamente: {len(result.get('generated_files', []))} archivos")
            return {
                "success": True,
                "message": f"🎯 NUEVO GENERADOR: Servicio multi-tabla '{service_config.service_name}' generado exitosamente con estructura INDIVIDUAL por tabla",
                "generated_files": result.get('generated_files', []),
                "files_count": len(result.get('generated_files', [])),
                "service_config": {
                    "name": service_config.service_name,
                    "tables_count": len(service_config.tables),
                    "relationships_count": len(service_config.relationships)
                }
            }
        else:
            error_msg = result.get('error', 'Error desconocido en la generación')
            print(f"❌ Error generando multi-tabla: {error_msg}")
            return {"success": False, "message": f"Error al generar servicio multi-tabla: {error_msg}"}
            
    except Exception as e:
        error_msg = f"Error al procesar configuración: {str(e)}"
        print(f"❌ {error_msg}")
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

# ============================================================================
# ENDPOINTS DE EJEMPLO Y DOCUMENTACIÓN
# ============================================================================

@router.get("/phase2-info")
async def get_phase2_info():
    """
    Información sobre las funcionalidades de Fase 2
    """
    return {
        "phase": "2",
        "version": "2.0.0",
        "new_features": {
            "many_to_many": "Relaciones many-to-many automáticas con tablas de unión",
            "unlimited_tables": "Soporte para N tablas (sin límites)",
            "complex_queries": "Queries complejas con múltiples JOINs",
            "aggregations": "Endpoints de agregación y estadísticas",
            "templates": "Templates predefinidos para casos comunes",
            "advanced_crud": "CRUDs avanzados con búsquedas complejas",
            "openapi_docs": "Documentación OpenAPI extendida"
        },
        "templates_available": Phase2Templates.get_template_info(),
        "upgrade_from_phase1": True
    }

@router.get("/templates")
async def get_available_templates():
    """
    Obtener todos los templates predefinidos disponibles
    """
    try:
        templates = Phase2Templates.get_all_templates()
        return {
            "success": True,
            "templates": templates,
            "templates_info": Phase2Templates.get_template_info(),
            "total_templates": len(templates)
        }
    except Exception as e:
        logger.error(f"Error obteniendo templates: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/template/{template_name}")
async def get_template_config(template_name: str):
    """
    Obtener configuración de un template específico
    """
    try:
        templates = Phase2Templates.get_all_templates()
        
        if template_name not in templates:
            return {
                "success": False,
                "error": f"Template '{template_name}' no encontrado",
                "available_templates": list(templates.keys())
            }
        
        return {
            "success": True,
            "template_name": template_name,
            "config": templates[template_name],
            "description": Phase2Templates.get_template_info().get(template_name, "")
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo template {template_name}: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/generate-from-template")
async def generate_from_template(template_data: Dict[str, Any]):
    """
    Generar sistema usando un template predefinido
    """
    try:
        template_name = template_data.get("template_name")
        customizations = template_data.get("customizations", {})
        
        if not template_name:
            return {"success": False, "error": "Nombre de template requerido"}
        
        # Obtener configuración base del template
        templates = Phase2Templates.get_all_templates()
        if template_name not in templates:
            return {
                "success": False,
                "error": f"Template '{template_name}' no encontrado",
                "available_templates": list(templates.keys())
            }
        
        # Aplicar personalizaciones
        template_config = templates[template_name].copy()
        
        # Aplicar personalizaciones básicas
        if "service_name" in customizations:
            template_config["service_name"] = customizations["service_name"]
        if "description" in customizations:
            template_config["description"] = customizations["description"]
        
        # Convertir a configuración de servicio
        service_config = create_service_config_from_json(template_config)
        
        # Validar configuración
        validation_errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        if validation_errors:
            return {
                "success": False,
                "error": "Errores de validación",
                "validation_errors": validation_errors
            }
        
        # Generar usando Fase 2
        generator = create_phase2_generator()
        result = await generator.generate_complete_system(service_config)
        
        if result["success"]:
            logger.info(f"✅ ÉXITO - Sistema generado desde template '{template_name}'")
            return {
                "success": True,
                "message": f"Sistema generado exitosamente desde template '{template_name}'",
                "template_used": template_name,
                "generated_files": result["generated_files"],
                "statistics": result["statistics"],
                "phase": "2"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error desconocido"),
                "template_used": template_name
            }
            
    except Exception as e:
        logger.error(f"Error generando desde template: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/generate-phase2")
async def generate_phase2_system(config_data: Dict[str, Any]):
    """
    Generar sistema completo usando funcionalidades de Fase 2
    """
    try:
        # Convertir a configuración de servicio
        service_config = create_service_config_from_json(config_data)
        
        # Validar configuración
        validation_errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        if validation_errors:
            return {
                "success": False,
                "error": "Errores de validación",
                "validation_errors": validation_errors
            }
        
        # Verificar que sea apropiado para Fase 2
        complexity = service_config.estimate_complexity()
        if complexity["many_to_many_count"] == 0 and complexity["tables_count"] <= 2:
            return {
                "success": False,
                "error": "Este sistema es simple. Considera usar Fase 1 o agregar relaciones many-to-many",
                "suggestion": "Usa /generate-multi-table para sistemas simples",
                "complexity_analysis": complexity
            }
        
        # Generar usando Fase 2
        generator = create_phase2_generator()
        result = await generator.generate_complete_system(service_config)
        
        if result["success"]:
            logger.info(f"✅ ÉXITO - Sistema Fase 2 generado: {service_config.service_name}")
            return {
                "success": True,
                "message": f"Sistema Fase 2 generado exitosamente: {service_config.service_name}",
                "generated_files": result["generated_files"],
                "junction_tables": result["junction_tables"],
                "complex_queries": result["complex_queries"],
                "statistics": result["statistics"],
                "phase": "2",
                "complexity_analysis": complexity
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error desconocido en generación Fase 2"),
                "phase": "2"
            }
            
    except Exception as e:
        logger.error(f"Error en generación Fase 2: {str(e)}")
        return {"success": False, "error": str(e), "phase": "2"}

@router.get("/phase2-example")
async def get_phase2_example():
    """
    Ejemplo de configuración para Fase 2 con relaciones many-to-many
    """
    return {
        "description": "Ejemplo de sistema Fase 2 con relaciones many-to-many",
        "example": Phase2Templates.ecommerce_system(),
        "features_demonstrated": [
            "Relaciones many-to-many (productos <-> etiquetas)",
            "Múltiples tablas (6 tablas)",
            "Campos avanzados (enum, decimal, email)",
            "Generación automática de tablas de unión",
            "CRUDs avanzados con búsquedas complejas"
        ],
        "phase": "2"
    }