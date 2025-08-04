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
from .generator_config import GENERATOR_CONFIG, VALIDATOR, PATH_MANAGER
from .generator_logger import main_logger, GenerationSession, error_handler
from .generator_factory import generator_factory

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
async def migraciones_page(
    request: Request,
    user_data: dict = Depends(require_auth_for_template)
):
    try:
        logger.info("Intentando renderizar template generar.html")
        logger.debug(f"User data keys: {user_data.keys()}")
        
        # Verificar si el archivo existe
        import os
        template_path = "sql_app/static/html/generar.html"
        if os.path.exists(template_path):
            logger.info(f"✅ Template file exists: {template_path}")
        else:
            logger.error(f"❌ Template file not found: {template_path}")
            
        return templates.TemplateResponse("html/generar.html", {
            "request": request, 
            **user_data  # Esto incluye user, user_count, activities, is_admin, is_authenticated, etc.
        })
    except Exception as e:
        logger.error(f"Error al renderizar template: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Fallback a una respuesta simple en caso de error
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content="""
        <html>
            <head><title>Error Temporal</title></head>
            <body>
                <h1>Generador de Aplicaciones</h1>
                <p>Error temporal al cargar la página. Por favor, inténtelo de nuevo.</p>
                <p>Error: """ + str(e) + """</p>
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