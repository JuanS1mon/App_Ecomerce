from fastapi import APIRouter,  status, Depends,Request
from starlette.responses import FileResponse
import os
import fileinput
import time
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(
    prefix="/generar",
    tags=["generar"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/")
async def read_root():

    return FileResponse('static/html/generar.html')


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
    
    if form_data.get('generate_schema') == 'true':
        print("Generar Schema")
        try:    
            generate_and_save_schema()
            generate_and_save_model()
        except:
            return {"message": "Error al generar y guardar los archivos"}
        
    if form_data.get('generate_route') == 'true':
        print("Generar Route")
        try:
            generate_and_save_route()
        except:
            return {"message": "Error al generar y guardar los archivos"}
    
    if form_data.get('generate_html_form') == 'true':
        print("Generar Formulario HTML")
        try:
            generate_html_form(module_name, field_names, field_types)
        except:
            return {"message": "Error al generar y guardar el formulario HTML"}

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

    

    # Genera el archivo de la ruta
def generate_route(module_name, field_names, field_types):

    # Genera las validaciones de campos requeridos
    field_validations = ' or '.join([f'{module_name}.{field_name} is None' for field_name in field_names[:2]])

    # Genera los argumentos para la función create_module_name
    create_args = ', '.join([f'{field_name}={module_name}.{field_name}' for field_name in field_names])

    route_code = f"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_{module_name} import {module_name}, {module_name}Read
from db.crud.Maestro.Crud_{module_name} import  create_{module_name} , get_{module_name}, gets_{module_name}, delete_{module_name}, get_{module_name}_{field_names[1]},update_{module_name}

router = APIRouter(
    prefix="/{module_name}",
    tags=["{module_name}"],
    responses={{status.HTTP_404_NOT_FOUND: {{"message": "ruta no encontrada"}}}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/{module_name}.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[{module_name}Read])
async def routes_Post_{module_name} ({module_name}: {module_name}, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if {field_validations}:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_{module_name} = get_{module_name}_{field_names[1]}(db, {field_names[1]}={module_name}.{field_names[1]})
    if resultado_{module_name} is None:
        db_{module_name} = create_{module_name}(db=db, {create_args})
        return db_{module_name}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: {field_names[1]} se encuentra registrado anteriormente en {module_name} ")

@router.get("/{{{field_names[0]}}}", response_model=list[{module_name}Read]) 
async def routes_get_{module_name}_{field_names[0]} ({field_names[0]}: {field_types[0]}, db: Session = Depends(get_db)):  
    db_{module_name} =  get_{module_name}(db, {field_names[0]}={field_names[0]})
    if not db_{module_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: {module_name} no encontrado")
    else:
        return db_{module_name}
    
@router.get("/", response_model=list[{module_name}Read]) 
async def routes_gets_{module_name}_all (db: Session = Depends(get_db)):  
    db_{module_name} = gets_{module_name}(db)
    if not db_{module_name}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: {module_name}s no encontrados")
    else:
        return db_{module_name}



@router.delete("/{{{field_names[0]}}}", response_model=list[{module_name}Read]) 
async def routes_delete_{module_name}_numero({field_names[0]}: {field_types[0]}, db: Session = Depends(get_db)):  
    resultado_{module_name} =  get_{module_name}(db, {field_names[0]}={field_names[0]})
    if not resultado_{module_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: {module_name} no encontrado")
    else:
        db_{module_name} = delete_{module_name}(db, {field_names[0]}={field_names[0]})
        return db_{module_name}

        
@router.put("/", response_model=list[{module_name}Read]) 
async def routes_update_{module_name}({module_name}: {module_name}, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if {field_validations}:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_{module_name}(db, codigo={module_name}.{field_names[0]})
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El {field_names[0]} {{{module_name}.{field_names[0]}}} no existe en la tabla {module_name}")
        else:
            resultado_{module_name} = get_{module_name}_{field_names[1]}(db, descripcion={module_name}.{field_names[1]})
            if resultado_{module_name} is None:
                db_{module_name} = update_{module_name}(db=db, {create_args})
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La {field_names[1]} {{{module_name}.{field_names[1]}}} ya se encuentra en la tabla {module_name}")
        return db_{module_name}
"""


    return route_code


def generate_and_save_route():
    module_name, field_names, field_types = DATOS_GENERALES
    # Genera el código de la ruta
    route_code = generate_route(module_name, field_names, field_types)

    # Define la ruta del archivo
    file_path = f"routers/Maestros/Route_{module_name}.py"

    # Verifica si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        # Abre el archivo en modo de escritura y guarda el código de la ruta
        with open(file_path, 'w') as file:
            file.write(route_code)
            print(f"Archivo {file_path} creado con éxito.")





def generate_crud_functions(module_name, field_names, field_types):
    # Comienza a construir el código de las funciones CRUD
    crud_code = f"from sqlalchemy.orm import Session\nfrom sqlalchemy import text\nfrom sqlalchemy.exc import SQLAlchemyError\nfrom fastapi import HTTPException,status\n\n"

    # Genera la función create
    crud_code += f"def create_{module_name}(db: Session, "
    crud_code += ", ".join([f"{field_name}: {field_type}" for field_name, field_type in zip(field_names, field_types)])
    crud_code += "):\n"
    crud_code += f"    try:\n"
    crud_code += f"        sql = text(\"\"\"INSERT INTO {module_name} ("
    crud_code += ", ".join(field_names)
    crud_code += ")\n"
    crud_code += "OUTPUT " + ", ".join([f"INSERTED.{field} AS {field}" for field in field_names])
    crud_code += f"\nVALUES (COALESCE((SELECT MAX({field_names[0]}) FROM {module_name}), 0) + 1, "
    crud_code += ", ".join([f":{field_name}" for field_name in field_names[1:]]) + ")\"\"\")\n"
    crud_code += f"        sql = db.execute(sql.params("
    crud_code += ", ".join([f"{field_name}={field_name}" for field_name in field_names])
    crud_code += "))\n"
    crud_code += f"        result = sql.fetchall()\n"
    crud_code += f"        db.commit()\n"
    crud_code += "        return [{"
    crud_code += ", ".join([f"'{field_name}': row[{i}]" for i, field_name in enumerate(field_names)])
    crud_code += "} for row in result] if result else None \n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=\"SQL: No se pudo guardar registro en {module_name}, intentelo de nuevo\")\n\n"

    # Genera las demás funciones CRUD (get, update, delete) de manera similar
    crud_code += f"def get_{module_name}(db: Session, {field_names[0]}: {field_types[0]}):\n"
    crud_code += f"    try:\n"
    crud_code += f"        if {field_names[0]} is not None:\n"
    crud_code += f"            query = text(\"SELECT "
    crud_code += ", ".join(field_names)
    crud_code += f" FROM {module_name} WHERE {field_names[0]} = :{field_names[0]}\")\n"
    crud_code += f"            sql = db.execute(query.params({field_names[0]}={field_names[0]}))\n"
    crud_code += f"        else:\n"
    crud_code += f"            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=\"{module_name} no encontrado\")\n"
    crud_code += f"        result = sql.fetchall()\n"
    crud_code += f"        return [{{"
    crud_code += ", ".join([f"'{field_name}': row[{i}]" for i, field_name in enumerate(field_names)])
    crud_code += "} for row in result] if result else None \n"
    crud_code += f"    except SQLAlchemyError:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=\" SQL: No se pudo obtener dato de {module_name}, intentelo de nuevo\")\n\n"
    # Genera la función gets
    crud_code += f"def gets_{module_name}(db: Session):\n"
    crud_code += f"    try:\n"
    crud_code += f"        query = text(\"SELECT "
    crud_code += ", ".join(field_names)
    crud_code += f" FROM {module_name}\")\n"
    crud_code += "        sql = db.execute(query)\n"
    crud_code += f"        result = sql.fetchall()\n"
    crud_code += f"        return [{{"
    crud_code += ", ".join([f"'{field_name}': row[{i}]" for i, field_name in enumerate(field_names)])
    crud_code += "} for row in result] if result else None \n"
    crud_code += f"    except SQLAlchemyError:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=\" SQL: No se pudo obtener dato de {module_name}, intentelo de nuevo\")\n\n"
    
    # Genera la función delete
    crud_code += f"def delete_{module_name}(db: Session, {field_names[0]}: {field_types[0]}):\n"
    crud_code += f"    try:\n"
    crud_code += f"        query = text(\"\"\"DELETE FROM {module_name}\n"
    crud_code += " OUTPUT " + ", ".join([f"DELETED.{field} AS {field}" for field in field_names])
    crud_code += f" WHERE {field_names[0]} = :{field_names[0]}  \"\"\")\n"
    crud_code += f"        sql = db.execute(query.params({field_names[0]}={field_names[0]}))\n"
    crud_code += f"        result = sql.fetchall()\n"
    crud_code += f"        db.commit()\n"
    crud_code += "        return [{" + ", ".join([f"'{field_name}': row[{i}]" for i, field_name in enumerate(field_names)]) + "} for row in result] if result else None\n"
    crud_code += f"    except SQLAlchemyError:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=404, detail=\"No se pudo eliminar\")\n\n"

    #genera la funcion get
    crud_code += f"def get_{module_name}_{field_names[1]}(db: Session, "
    crud_code += f"{field_names[1]}: str):\n"
    crud_code += f"    try:\n"
    crud_code += f"        if {field_names[1]} is not None:\n"
    crud_code += f"            query = text(\"SELECT " + ", ".join(field_names) + f" FROM {module_name} WHERE {field_names[1]} LIKE :{field_names[1]}\")\n"
    crud_code += f"            sql = db.execute(query.params({field_names[1]}='%' + {field_names[1]} + '%'))\n"
    crud_code += f"        else:\n"
    crud_code += f"            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=\"{module_name} no encontrado\")\n"
    crud_code += f"        result = sql.fetchall()\n"
    crud_code += f"        if not result:\n"
    crud_code += f"            return None\n"
    crud_code += f"        return [{{"
    crud_code += ", ".join([f"'{field_name}': row[{i}]" for i, field_name in enumerate(field_names)])
    crud_code += "} for row in result] if result else None\n"
    crud_code += f"    except Exception as e:\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))\n\n"
    
    #genera la funcion Update
    crud_code += f"def update_{module_name}(db: Session, "
    crud_code += ", ".join([f"{field_name}: {field_type}" for field_name, field_type in zip(field_names, field_types)])
    crud_code += "):\n"
    crud_code += f"    try:\n"
    crud_code += f"        query = text(\"\"\"UPDATE {module_name} SET "
    crud_code += ", ".join([f"{field_name} = :{field_name}" for field_name in field_names[1:]])
    crud_code += "\nOUTPUT " + ", ".join([f"INSERTED.{field} AS {field}" for field in field_names])
    crud_code += f"\nWHERE {field_names[0]} = :{field_names[0]}"
    crud_code += "\"\"\")\n"
    crud_code += f"        sql = db.execute(query.params("
    crud_code += ", ".join([f"{field_name}={field_name}" for field_name in field_names])
    crud_code += "))\n"
    crud_code += f"        result = sql.fetchall()\n"
    crud_code += f"        db.commit()\n"
    crud_code += "        return [{" + ", ".join([f"'{field_name}': row[{i}]" for i, field_name in enumerate(field_names)]) + "} for row in result] if result else None\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f\" Route: descripcion no se pudo actualizar el codigo {{codigo}} en Familias \")\n\n"
    
    return crud_code





def generate_and_save_crud():
    module_name, field_names, field_types = DATOS_GENERALES
    # Genera el código CRUD
    crud_code = generate_crud_functions(module_name, field_names, field_types)

    # Define la ruta del archivo
    file_path = f"db/crud/Maestro/Crud_{module_name}.py"

    # Verifica si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        # Abre el archivo en modo de escritura y guarda el código CRUD
        with open(file_path, 'w') as file:
            file.write(crud_code)
            print(f"Archivo {file_path} creado con éxito.")



def generate_schema(module_name, field_names, field_types):
    # Comienza a construir el código del esquema
    schema_code = f"from pydantic import BaseModel, Field\nfrom typing import Optional\nfrom datetime import date\n\n\n"
    schema_code += f"class {module_name}(BaseModel):\n\n"

    # Añade cada campo al esquema
    for i, (field_name, field_type) in enumerate(zip(field_names, field_types)):
        if i < 2:  # Los dos primeros campos son obligatorios
            schema_code += f"    {field_name}: {field_type}\n"
        else:  # Los demás campos son opcionales con un valor por defecto
            default_value = '0' if field_type in ['int', 'bool', 'float'] else '"vacio"'
            schema_code += f"    {field_name}: Optional[{field_type}] = {default_value}\n"

    # Añade el esquema de lectura
    schema_code += f"\nclass {module_name}Read(BaseModel):\n"
    for i, (field_name, field_type) in enumerate(zip(field_names, field_types)):
        if i < 2:  # Los dos primeros campos son obligatorios
            schema_code += f"    {field_name}: {field_type}\n"
        else:  # Los demás campos son opcionales con un valor por defecto
            default_value = '0' if field_type in ['int', 'bool', 'float'] else '"vacio"'
            schema_code += f"    {field_name}: Optional[{field_type}] = {default_value}\n"

    return schema_code


def generate_and_save_schema():
    module_name, field_names, field_types = DATOS_GENERALES
    # Genera el código del esquema
    schema_code = generate_schema(module_name, field_names, field_types)

    # Define la ruta del archivo
    file_path = f"db/schemas/Maestro/Schema_{module_name}.py"

    # Verifica si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        # Abre el archivo en modo de escritura y guarda el código del esquema
        with open(file_path, 'w') as file:
            file.write(schema_code)
            print(f"Archivo {file_path} creado con éxito.")



def generate_model(module_name, field_names, field_types):
    # Comienza a construir el código del modelo
    model_code = f"from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float\nfrom ..database import Base\n\n\n"
    model_code += f"class {module_name}(Base):\n"
    model_code += f"    __tablename__ = '{module_name.lower()}'\n\n"

    # Añade cada campo al modelo
    for i, (field_name, field_type) in enumerate(zip(field_names, field_types)):
        if field_type == 'int':
            model_code += f"    {field_name} = Column(Integer, primary_key=True, index=True, default=0)\n"
        elif field_type == 'str':
            model_code += f"    {field_name} = Column(NVARCHAR(50), default=' ')\n"
        elif field_type == 'bool':
            model_code += f"    {field_name} = Column(Boolean, default=False)\n"
        elif field_type == 'float':
            model_code += f"    {field_name} = Column(Float, default=0.0)\n"

    return model_code

def generate_and_save_model():
    module_name, field_names, field_types = DATOS_GENERALES
    # Genera el código del modelo
    model_code = generate_model(module_name, field_names, field_types)

    # Define la ruta del archivo
    file_path = f"db/models/{module_name}.py"

    # Verifica si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        # Abre el archivo en modo de escritura y guarda el código del modelo
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



from yattag import Doc
import os


from bs4 import BeautifulSoup
def generate_html_form(module_name, field_names, field_types):
    doc, tag, text, line = Doc().ttl()

    with tag('html'):
        with tag('head'):
            line('title', 'Admin')
            doc.stag('link', rel='stylesheet', type='text/css', href='/static/css/styles.css')
            with tag('script', type='text/javascript'):
                doc.asis('''
            function myFunction(event) {
                event.preventDefault();

                var formData = new FormData(event.target);
                var formObject = {};

                formData.forEach(function(value, key){
                    formObject[key] = value;
                });

                fetch('/''' + module_name + '''/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formObject)
                }).then(response => {
                    if (!response.ok) {  // Si la respuesta no es ok (es decir, el código de estado no es 2xx)
                        return response.json().then(json => { throw new Error(json.detail); });  // Lanza un error con el detalle de la respuesta
                    }
                    return response.json();
                })
                .then(data => alert("Formulario enviado!"))
                .catch(error => alert(error));  // Muestra el error en un alerta
            }

            window.onload = function() {
                fetch("/''' + module_name + '''/")
                    .then(response => response.json())
                .then(data => {
                    var table = document.querySelector('.table tbody');
                    data.forEach(item => {
                        var row = document.createElement('tr');
                        for (var property in item) {
                            var cell = document.createElement('td');
                            cell.textContent = item[property];
                            row.appendChild(cell);
                        }

                        var deleteCell = document.createElement('td');  // Crea una nueva celda para el botón de eliminar
                        var deleteButton = document.createElement('button');  // Crea el botón de eliminar
                        deleteButton.textContent = 'X';
                        deleteButton.className = 'remove_small';
                        deleteButton.dataset.code = item.codigo;  // Agrega el valor del código como un atributo de datos personalizado
                        deleteButton.addEventListener('click', deleteItem);  // Vincula la función deleteItem al evento click del botón
                        deleteCell.appendChild(deleteButton);  // Agrega el botón a la celda
                        row.appendChild(deleteCell);  // Agrega la celda a la fila

                        table.appendChild(row);
                });
            });

            fetch('/static/head.html')
            .then(response => response.text())
            .then(data => {
            document.getElementById('nav').innerHTML = data;
            })
            .catch(error => {
            console.error('Error:', error);
            });
            };

            fetch('/static/footer.html')
            .then(response => response.text())
            .then(data => {
            document.getElementById('footer').innerHTML = data;
            })
            .catch(error => {
            console.error('Error:', error);
            });


        function deleteItem(event) {
            var code = event.target.dataset.code;
            fetch("/''' + module_name + '''/" + code, {
                method: 'DELETE'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al eliminar el elemento');
                }
                return response.json();
            })
            .then(data => {
                alert('El elemento se elimino correctamente');
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }
        ''')
        with tag('body'):
            with tag('nav',  id='nav'):
                with tag('ul'):
                    text('<!-- Aquí va el código de la barra de navegación -->')
            with tag('div', id='content'):
                with tag('form', onsubmit="myFunction(event)"):
                    with tag('h1'):
                        text('Formulario para ' + module_name)
                    for field_name, field_type in zip(field_names, field_types):
                        with tag('label'):
                            text(f'{field_name}: ')
                        if field_type == 'str':
                            field_type = 'text'
                        elif field_type in ['int', 'float']:
                            field_type = 'number'
                        elif field_type == 'bool':
                            field_type = 'checkbox'
                        doc.stag('input', type = field_type, name = field_name)
                    doc.stag('input', type = 'submit', value = 'Guardar')
    with tag('div', klass='container'):
        with tag('table', klass='table'):
            with tag('thead'):
                with tag('tr'):
                    for field_name in field_names:
                        with tag('th'):
                            text(field_name)
            with tag('tbody'):
                with tag('tr'):
                    for _ in field_names:
                        with tag('td'):
                            text('')
        with tag('footer', id='footer'):
            doc.asis('<!-- Aquí se insertará el contenido del archivo footer.html -->')

    html_content = doc.getvalue()

    # Formatea el contenido HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    html_content = soup.prettify()

    print(html_content)
    output_dir = "static/html"

    # Define la ruta del archivo
    file_path = f"{output_dir}/{module_name}.html"

    # Verifica si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe.")
    else:
        # Abre el archivo en modo de escritura y guarda el contenido HTML
        with open(file_path, 'w') as file:
            file.write(html_content)
            print(f"Archivo {file_path} creado con éxito.")