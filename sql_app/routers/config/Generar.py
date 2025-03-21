#generar.py
from fastapi import APIRouter, status, Depends, Request
from starlette.responses import FileResponse
import os
import fileinput
from fastapi.security import OAuth2PasswordBearer
from Services.security.security import get_current_user
from .Generar_Funciones.Generar_Routes import generate_route
from .Generar_Funciones.Generar_Cruds import generate_crud_functions
from .Generar_Funciones.Generar_Schema import generate_schema
from .Generar_Funciones.Generar_Models import generate_model
from .Generar_Funciones.Generar_Html import generate_html_form
from .Generar_Funciones.Generar_Test import generate_tests
from fastapi.templating import Jinja2Templates

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="static/html")

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
    generate_route = form_data.get('generate_route') == 'true'
    generate_schema = form_data.get('generate_schema') == 'true'
    generate_html_form_opt = form_data.get('generate_html_form') == 'true'
    generate_tests = form_data.get('generate_tests') == 'true'
    agregar_rutas = form_data.get('agregar_rutas') == 'true'
    generate_service = form_data.get('generate_service') == 'true'  # Opción de servicio
    
    # Si generate_service está marcado, no usamos generate_crud
    if generate_service:
        generate_crud = False
        try:
            generate_and_save_service(module_name, field_names, field_types)
        except Exception as e:
            return {"message": f"Error al generar y guardar el servicio: {str(e)}"}
    elif generate_crud:
        generate_and_save_crud(module_name, field_names, field_types)
        
    if generate_route:
        try:
            generate_and_save_route(module_name, field_names, field_types)
        except Exception as e:
            return {"message": f"Error al generar y guardar las rutas: {str(e)}"}
        
        
    if generate_schema:
        try:    
            generate_and_save_schema(module_name, field_names, field_types)
            generate_and_save_model(module_name, field_names, field_types)
        except Exception as e:
            return {"message": "Error al generar y guardar los esquemas y modelos"}

    if generate_html_form_opt:
        try:
            html_content = generate_html_form(module_name, field_names, field_types)
            save_html_form(module_name, html_content)
        except Exception as e:
            return {"message": "Error al generar y guardar el formulario HTML"}

    if generate_tests:
        try:
            generate_and_save_tests(module_name, field_names, field_types)
        except Exception as e:
            return {"message": "Error al generar y guardar las pruebas"}
    
    if agregar_rutas:
        add_new_route_to_main(module_name)
    
    return {"message": "Generación completada exitosamente"}

def generate_and_save_service(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    # Creamos la estructura de directorios si no existe
    service_dir = f"Services/{module_name}"
    os.makedirs(service_dir, exist_ok=True)
    
    # Generar todos los componentes dentro de la carpeta de servicios
    try:
        # 1. Generar y guardar el servicio (CRUD con SQL)
        from .Generar_Funciones.Generar_Cruds_sql import generate_crud_functions
        service_code = generate_crud_functions(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/service_{module_name}.py", service_code)
        
        # 2. Generar y guardar las rutas
        from .Generar_Funciones.Generar_Routes import generate_route
        route_code = generate_route(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/route_{module_name}.py", route_code)
        
        # 3. Generar y guardar los schemas
        from .Generar_Funciones.Generar_Schema import generate_schema
        schema_code = generate_schema(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/schema_{module_name}.py", schema_code)
        
        # 4. Generar y guardar el modelo
        from .Generar_Funciones.Generar_Models import generate_model
        model_code = generate_model(module_name, field_names, field_types)
        save_file_to_service(f"{service_dir}/model_{module_name}.py", model_code)
        
        print(f"Servicio completo generado exitosamente en {service_dir}")
    except Exception as e:
        print(f"Error al generar el servicio completo: {e}")
        raise

def save_file_to_service(file_path, content):
    """
    Función auxiliar para guardar archivos en la carpeta de servicios
    """
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w') as file:
                file.write(content)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")
            raise

def generate_and_save_route(module_name, field_names, field_types):
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    route_code = generate_route(module_name, field_names, field_types)

    file_path = f"routers/Maestros/Route_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        try:
            with open(file_path, 'w') as file:
                file.write(route_code)
                print(f"Archivo {file_path} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar el archivo {file_path}: {e}")


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