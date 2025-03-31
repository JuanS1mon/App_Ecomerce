#generar.py
from fastapi import APIRouter, status, Depends, Request
from starlette.responses import FileResponse
import os
import fileinput
import logging
import traceback
from fastapi.security import OAuth2PasswordBearer
from Services.security.security import get_current_user
from .Generar_Funciones.Generar_Routes import generate_route
from .Generar_Funciones.Generar_Cruds import generate_crud_functions
from .Generar_Funciones.Generar_Schema import generate_schema
from .Generar_Funciones.Generar_Models import generate_model
from .Generar_Funciones.Generar_Html import generate_html_form
from .Generar_Funciones.Generar_Test import generate_tests
from .Generar_Funciones.Generar_Html_service import generate_html_for_service
from fastapi.templating import Jinja2Templates


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="static/html")

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

router = APIRouter(
    include_in_schema=False ,  # Oculta todas las rutas de este router en la documentación
    prefix="/generar",
    tags=["generar"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/")
async def migraciones_page(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    return templates.TemplateResponse("generar.html", {"request": request, "user": current_user})

@router.post("/generate")
async def generate(request: Request):
    form_data = await request.form()
    module_name = form_data["module_name"]
    field_names = form_data.getlist("field_names[]")
    field_types = form_data.getlist("field_types[]")

    # Procesar opciones elegidas por el usuario
    generate_crud = form_data.get('generate_crud') == 'true'
    generate_route_opt = form_data.get('generate_route') == 'true'
    generate_schema_opt = form_data.get('generate_schema') == 'true'
    generate_html_form_opt = form_data.get('generate_html_form') == 'true'
    generate_tests_opt = form_data.get('generate_tests') == 'true'
    agregar_rutas = form_data.get('agregar_rutas') == 'true'
    generate_service = form_data.get('generate_service') == 'true'  # Opción de servicio
    
    result_message = "Generación completada exitosamente"
    
    # Si generate_service está marcado, no usamos generate_crud
    if generate_service:
        generate_crud = False
        try:
            success = generate_and_save_service(module_name, field_names, field_types)
            if success:
                result_message += f". Servicio '{module_name}' generado y registrado."
            else:
                return {"message": f"Error al generar el servicio '{module_name}'"}
        except Exception as e:
            logger.error(f"Error al generar servicio: {str(e)}")
            traceback.print_exc()
            return {"message": f"Error al generar y guardar el servicio: {str(e)}"}
    elif generate_crud:
        generate_and_save_crud(module_name, field_names, field_types)
        
        # Generación individual según opciones
        if generate_route_opt:
            generate_and_save_route(module_name, field_names, field_types)
            if agregar_rutas:
                add_new_route_to_main(module_name)
        
        if generate_schema_opt:
            generate_and_save_schema(module_name, field_names, field_types)
            
        if generate_html_form_opt:
            html_content = generate_html_form(module_name, field_names, field_types)
            save_html_form(module_name, html_content)
            
        if generate_tests_opt:
            generate_and_save_tests(module_name, field_names, field_types)
    
    return {"message": result_message}
def generate_and_save_service(module_name, field_names, field_types):
    """
    Genera y guarda un servicio completo (modelo, schema, crud, rutas).
    Devuelve True si fue exitoso, False en caso contrario.
    """
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    # Creamos la estructura de directorios si no existe
    service_dir = f"Services/{module_name}"
    os.makedirs(service_dir, exist_ok=True)
    
    # Generar todos los componentes dentro de la carpeta de servicios
    try:
        # 1. Generar y guardar el servicio (CRUD con SQL)
        from .Generar_Funciones.Generar_Cruds_service import generate_crud_functions
        service_code = generate_crud_functions(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/service_{module_name}.py", service_code)
        
        # 2. Generar y guardar las rutas
        from .Generar_Funciones.Generar_Routes_service import generate_route
        route_code = generate_route(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/route_{module_name}.py", route_code)
        
        # 3. Generar y guardar los schemas
        from .Generar_Funciones.Generar_Schema_serice import generate_schema
        schema_code = generate_schema(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/schema_{module_name}.py", schema_code)
        
        # 4. Generar y guardar el modelo
        from .Generar_Funciones.Generar_Models_service import generate_model
        model_code = generate_model(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/model_{module_name}.py", model_code)
        
        # 5. Generar archivo __init__.py para hacer el servicio importable
        module_name_cap = module_name.capitalize()
        init_code = generate_init_file(module_name, module_name_cap)
        save_file_to_service(f"{service_dir}/__init__.py", init_code)
        
        # 6. Generar el archivo HTML para la ruta /pagina
        html_content = generate_html_for_service(module_name, field_names, field_types)
        html_dir = "static/html"
        os.makedirs(html_dir, exist_ok=True)
        html_path = f"{html_dir}/{module_name}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Archivo HTML {html_path} generado para la ruta /pagina")
        
        # 7. Registrar el servicio en el gestor de servicios
        register_service_in_manager(module_name)
        
        logger.info(f"Servicio completo generado exitosamente en {service_dir}")
        return True
    except Exception as e:
        logger.error(f"Error al generar el servicio completo: {str(e)}")
        traceback.print_exc()
        return False

def save_file_to_service(file_path, content):
    """
    Guarda el contenido en el archivo especificado, creando directorios si es necesario.
    """
    try:
        # Asegurar que exista el directorio
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        
        # Escribir el archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Archivo {file_path} guardado exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error al guardar el archivo {file_path}: {str(e)}")
        return False

def register_service_in_manager(module_name):
    """
    Registra el nuevo servicio en el ServicesManager
    """
    try:
        # Importamos el gestor de servicios
        from routers.config import service_manager
        
        # El ID del servicio según la convención del gestor
        service_id = f"{module_name}.route_{module_name}"
        
        if service_manager.services_manager is None:
            logger.warning("El gestor de servicios no está inicializado")
            return False
            
        # También registrar en ServicesManager para su gestión futura
        services_manager = service_manager.services_manager
        
        # Forzar un nuevo escaneo para detectar el nuevo servicio
        services_manager.scan_services()
        
        # Registrar y activar el servicio
        if service_id not in services_manager.active_services:
            services_manager.active_services[service_id] = True
            
        # Intentar registrar el servicio inmediatamente
        try:
            success = services_manager.register_service(service_id)
            logger.info(f"Servicio {service_id} registro inmediato: {'exitoso' if success else 'fallido'}")
        except Exception as e:
            logger.warning(f"No se pudo registrar inmediatamente el servicio {service_id}: {str(e)}")
            
        # Guardar el estado actualizado
        services_manager.save_state()
        
        logger.info(f"Servicio {service_id} registrado en el gestor de servicios")
        return True
    except Exception as e:
        logger.error(f"Error al registrar el servicio en el gestor: {str(e)}")
        traceback.print_exc()
        return False

def generate_init_file(module_name, module_name_cap):
    """
    Genera el contenido del archivo __init__.py para el servicio
    """
    init_code = f"""# Archivo __init__.py para el servicio {module_name}
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_{module_name} import {module_name_cap}
from .schema_{module_name} import {module_name_cap}Create, {module_name_cap}Update, {module_name_cap}Read
from .service_{module_name} import (
    create_{module_name}, 
    get_{module_name}, 
    gets_{module_name},
    update_{module_name},
    delete_{module_name}
)
from .route_{module_name} import router

# Para facilitar la inclusión del router en la aplicación principal
{module_name}_router = router

__all__ = [
    '{module_name_cap}',
    '{module_name_cap}Create',
    '{module_name_cap}Update', 
    '{module_name_cap}Read',
    'create_{module_name}',
    'get_{module_name}',
    'gets_{module_name}',
    'update_{module_name}',
    'delete_{module_name}',
    'router',
    '{module_name}_router'
]
"""
    return init_code

def generate_and_save_route(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    route_code = generate_route(module_name, field_names, field_types)

    file_path = f"routers/Maestros/Route_{module_name}.py"

    if os.path.exists(file_path):
        logger.warning(f"El archivo {file_path} ya existe.")
    else:
        try:
            # Asegurar que exista el directorio
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as file:
                file.write(route_code)
                logger.info(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            logger.error(f"Error al guardar el archivo {file_path}: {e}")

def generate_and_save_crud(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    crud_code = generate_crud_functions(module_name, field_names, field_types)

    file_path = f"db/crud/Maestro/Crud_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w') as file:
                file.write(crud_code)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")

def generate_and_save_schema(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    schema_code = generate_schema(module_name, field_names, field_types)

    file_path = f"db/schemas/Maestro/Schema_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w') as file:
                file.write(schema_code)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")

def generate_and_save_model(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    model_code = generate_model(module_name, field_names, field_types)

    file_path = f"db/models/{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w') as file:
                file.write(model_code)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")

def save_html_form(module_name, html_content):
    import os
    output_dir = "static/html"
    os.makedirs(output_dir, exist_ok=True)  # Crear el directorio si no existe

    file_path = f"{output_dir}/{module_name}.html"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")

def generate_and_save_tests(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    test_code = generate_tests(module_name, field_names, field_types)

    file_path = f"tests/test_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w') as file:
                file.write(test_code)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")

def add_new_route_to_main(new_route):
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
    except Exception as e:
        print(f"Error al agregar la nueva ruta al main.py: {e}")