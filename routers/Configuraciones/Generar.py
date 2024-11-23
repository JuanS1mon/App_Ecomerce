from fastapi import APIRouter,  status, Depends,Request
from starlette.responses import FileResponse
import os
import fileinput
import time
from fastapi.security import OAuth2PasswordBearer
from Services.security.security import get_current_user
from  .Generar_Funciones.Generar_Routes import generate_route 
from  .Generar_Funciones.Generar_Cruds import generate_crud_functions
from  .Generar_Funciones.Generar_Schema import generate_schema
from  .Generar_Funciones.Generar_Models import generate_model
from  .Generar_Funciones.Generar_Html import generate_html_form
from  .Generar_Funciones.Generar_Test import generate_tests
from fastapi.templating import Jinja2Templates


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="static/html")

router = APIRouter(
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
    global DATOS_GENERALES
    DATOS_GENERALES = (module_name, field_names, field_types)
    
    if form_data.get('generate_crud') == 'true':
        print("Generar CRUD")
        generate_and_save_crud()
    
    if form_data.get('generate_route') == 'true':
        print("Generar Route")
        try:
            generate_and_save_route()
        except:
            return {"message": "Error al generar y guardar los archivos"}
    
    if form_data.get('generate_schema') == 'true':
        print("Generar Schema")
        try:    
            generate_and_save_schema()
            generate_and_save_model()
        except:
            return {"message": "Error al generar y guardar los archivos"}
        
    if form_data.get('generate_html_form') == 'true':
        print("Generar Formulario HTML")
        try:
            html_content = generate_html_form(module_name, field_names, field_types)
            save_html_form(module_name, html_content)
        except:
            return {"message": "Error al generar y guardar el formulario HTML"}

    if form_data.get('generate_tests') == 'true':
        print("Generar Pruebas")
        try:
            generate_and_save_tests()
        except:
            return {"message": "Error al generar y guardar las pruebas"}

    # Preguntar al usuario si desea agregar las nuevas rutas al archivo main
    
    time.sleep(5)  # pausa de 5 segundos
    agregar_rutas = input("¿Desea agregar las nuevas rutas al archivo main? (s/n): ")
        
    if agregar_rutas.lower() == "s":
        add_new_route_to_main(module_name)

    # Convertir los datos del formulario en un diccionario
    data_dict = {
        "module_name": module_name,
        "field_names": field_names,
        "field_types": field_types,
    }

    return data_dict
#////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////

#generar y guardar el código de las rutas (endpoints) para un módulo dado.
def generate_and_save_route():
    """
    Genera y guarda el código de las rutas (endpoints) para un módulo dado.
    """
    module_name, field_names, field_types = DATOS_GENERALES
    # Convertir a minúsculas
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    route_code = generate_route(module_name, field_names, field_types)

    file_path = f"routers/Maestros/Route_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        with open(file_path, 'w') as file:
            file.write(route_code)
            print(f"Archivo {file_path} creado con éxito.")

#generar y guardar el código CRUD para un módulo dado.
def generate_and_save_crud():
    """
    Genera y guarda el código CRUD para un módulo dado.
    """
    module_name, field_names, field_types = DATOS_GENERALES
    # Convertir a minúsculas
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    crud_code = generate_crud_functions(module_name, field_names, field_types)

    file_path = f"db/crud/Maestro/Crud_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        with open(file_path, 'w') as file:
            file.write(crud_code)
            print(f"Archivo {file_path} creado con éxito.")

def generate_and_save_schema():
    """
    Genera y guarda el esquema Pydantic para un módulo dado.
    """
    module_name, field_names, field_types = DATOS_GENERALES
    # Convertir a minúsculas
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    schema_code = generate_schema(module_name, field_names, field_types)

    file_path = f"db/schemas/Maestro/Schema_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        with open(file_path, 'w') as file:
            file.write(schema_code)
            print(f"Archivo {file_path} creado con éxito.")

#generar y guardar el modelo SQLAlchemy para un módulo dado.
def generate_and_save_model():
    """
    Genera y guarda el modelo SQLAlchemy para un módulo dado.
    """
    module_name, field_names, field_types = DATOS_GENERALES
    # Convertir a minúsculas
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    model_code = generate_model(module_name, field_names, field_types)

    file_path = f"db/models/{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        with open(file_path, 'w') as file:
            file.write(model_code)
            print(f"Archivo {file_path} creado con éxito.")

def add_new_route_to_main(new_route):
    with fileinput.FileInput('main.py', inplace=False) as file:
        lines = list(file)
    for i, line in enumerate(lines):
        if line.strip().startswith('from routers.Maestros import'):
            lines[i] = line.strip() + ', Route_'+new_route + '\n'
        if '#Maestros' in line:
            last_maestros_index = i
    lines.insert(last_maestros_index + 1, 'app.include_router(Route_' + new_route + '.router)\n')
        
    with open('main.py', 'w') as file:
        file.writelines(lines)


def save_html_form(module_name, html_content):
    import os
    output_dir = "static/html"
    os.makedirs(output_dir, exist_ok=True)  # Crear el directorio si no existe

    file_path = f"{output_dir}/{module_name}.html"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
            print(f"Archivo {file_path} creado con éxito.")


def generate_and_save_tests():
    """
    Genera y guarda el código de pruebas para un módulo dado.
    """
    module_name, field_names, field_types = DATOS_GENERALES
    # Convertir a minúsculas
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    test_code = generate_tests(module_name, field_names, field_types)

    file_path = f"tests/test_{module_name}.py"

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        with open(file_path, 'w') as file:
            file.write(test_code)
            print(f"Archivo {file_path} creado con éxito.")