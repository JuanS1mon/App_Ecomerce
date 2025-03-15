from fastapi import APIRouter, HTTPException, status, Depends,Request
from starlette.responses import HTMLResponse,FileResponse
import os
import fileinput
import time
from ..usuarios import get_current_user
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
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
    crud_code = f"from sqlalchemy.orm import Session\nfrom sqlalchemy.exc import SQLAlchemyError\nfrom fastapi import HTTPException, status\nfrom models import {module_name.capitalize()}\n\n"

    # Genera la función create
    crud_code += f"def create_{module_name}(db: Session, "
    crud_code += ", ".join([f"{field_name}: {field_type}" for field_name, field_type in zip(field_names, field_types)])
    crud_code += "):\n"
    crud_code += f"    try:\n"
    crud_code += f"        new_record = {module_name.capitalize()}("
    crud_code += ", ".join([f"{field_name}={field_name}" for field_name in field_names])
    crud_code += ")\n"
    crud_code += f"        db.add(new_record)\n"
    crud_code += f"        db.commit()\n"
    crud_code += f"        db.refresh(new_record)\n"
    crud_code += f"        return new_record\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n"

    # Genera la función get
    crud_code += f"def get_{module_name}(db: Session, {field_names[0]}: {field_types[0]}):\n"
    crud_code += f"    try:\n"
    crud_code += f"        record = db.query({module_name.capitalize()}).filter({module_name.capitalize()}.{field_names[0]} == {field_names[0]}).first()\n"
    crud_code += f"        if not record:\n"
    crud_code += f"            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"{module_name.capitalize()} no encontrado\")\n"
    crud_code += f"        return record\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n"

    # Genera la función gets
    crud_code += f"def gets_{module_name}(db: Session):\n"
    crud_code += f"    try:\n"
    crud_code += f"        records = db.query({module_name.capitalize()}).all()\n"
    crud_code += f"        return records\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n"

    # Genera la función delete
    crud_code += f"def delete_{module_name}(db: Session, {field_names[0]}: {field_types[0]}):\n"
    crud_code += f"    try:\n"
    crud_code += f"        record = db.query({module_name.capitalize()}).filter({module_name.capitalize()}.{field_names[0]} == {field_names[0]}).first()\n"
    crud_code += f"        if not record:\n"
    crud_code += f"            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"{module_name.capitalize()} no encontrado\")\n"
    crud_code += f"        db.delete(record)\n"
    crud_code += f"        db.commit()\n"
    crud_code += f"        return record\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n"

    # Genera la función get con filtro
    crud_code += f"def get_{module_name}_{field_names[1]}(db: Session, {field_names[1]}: str):\n"
    crud_code += f"    try:\n"
    crud_code += f"        records = db.query({module_name.capitalize()}).filter({module_name.capitalize()}.{field_names[1]}.like(f'%{{{field_names[1]}}}%')).all()\n"
    crud_code += f"        if not records:\n"
    crud_code += f"            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"{module_name.capitalize()} no encontrado\")\n"
    crud_code += f"        return records\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n"

    # Genera la función update
    crud_code += f"def update_{module_name}(db: Session, "
    crud_code += ", ".join([f"{field_name}: {field_type}" for field_name, field_type in zip(field_names, field_types)])
    crud_code += "):\n"
    crud_code += f"    try:\n"
    crud_code += f"        record = db.query({module_name.capitalize()}).filter({module_name.capitalize()}.{field_names[0]} == {field_names[0]}).first()\n"
    crud_code += f"        if not record:\n"
    crud_code += f"            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"{module_name.capitalize()} no encontrado\")\n"
    crud_code += f"        for key, value in {{"
    crud_code += ", ".join([f"'{field_name}': {field_name}" for field_name in field_names])
    crud_code += "}.items():\n"
    crud_code += f"            setattr(record, key, value)\n"
    crud_code += f"        db.commit()\n"
    crud_code += f"        db.refresh(record)\n"
    crud_code += f"        return record\n"
    crud_code += f"    except SQLAlchemyError as e:\n"
    crud_code += f"        db.rollback()\n"
    crud_code += f"        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n"

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
    model_code = f"from sqlalchemy import Column, Integer, String, Boolean, Float\nfrom ..database import Base\n\n\n"
    model_code += f"class {module_name}(Base):\n"
    model_code += f"    __tablename__ = '{module_name.lower()}'\n\n"

    # Añade cada campo al modelo
    for i, (field_name, field_type) in enumerate(zip(field_names, field_types)):
        if field_type == 'int':
            model_code += f"    {field_name} = Column(Integer, primary_key=True, index=True, default=0)\n"
        elif field_type == 'str':
            model_code += f"    {field_name} = Column(String, default=' ')\n"
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
            line('meta', charset="UTF-8")
            doc.stag('meta', name="viewport", content="width=device-width, initial-scale=1.0")
            line('title', module_name)
            doc.stag('link', rel='stylesheet', href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css')
            doc.stag('script', src='https://code.jquery.com/jquery-3.5.1.min.js')
            doc.stag('script', src='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js')
            doc.stag('script', src='https://unpkg.com/xlsx/dist/xlsx.full.min.js')
            doc.stag('script', src='https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.2/FileSaver.min.js')
            with tag('script'):
                doc.asis('''
                $(function(){
                    $("#navbar").load("../static/head.html"); 
                    $("#footer").load("../static/footer.html"); 
                });
                ''')
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

                    fetch('/departamentos/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formObject)
                    }).then(response => {
                        if (!response.ok) {
                            return response.json().then(json => { throw new Error(json.detail); });
                        }
                        return response.json();
                    })
                    .then(data => alert("Formulario enviado!"))
                    .catch(error => alert(error));
                }

                window.onload = function() {
                    fetch("http://localhost:8000/departamentos/")
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

                            var deleteCell = document.createElement('td');
                            var deleteButton = document.createElement('button');
                            deleteButton.textContent = 'X';
                            deleteButton.className = 'remove_small';
                            deleteButton.dataset.code = item.codigo;
                            deleteButton.addEventListener('click', deleteItem);
                            deleteCell.appendChild(deleteButton);
                            row.appendChild(deleteCell);

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
                    fetch("http://localhost:8000/departamentos/" + code, {
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

                $(function() {
                    $("#export").click(function() {
                        var wb = XLSX.utils.book_new();
                        var ws = XLSX.utils.table_to_sheet(document.querySelector('.table'));

                        ws['A1'].s = { fill: { fgColor: { rgb: "FFFF00" } }, font: { bold: true } };
                        ws['B1'].s = { fill: { fgColor: { rgb: "FFFF00" } }, font: { bold: true } };

                        XLSX.utils.book_append_sheet(wb, ws, "Sheet JS");

                        var wbout = XLSX.write(wb, {bookType:'xlsx', bookSST:true, type: 'binary'});
                        saveAs(new Blob([s2ab(wbout)],{type:"application/octet-stream"}), 'test.xlsx');
                    });
                });

                function s2ab(s) {
                    var buf = new ArrayBuffer(s.length);
                    var view = new Uint8Array(buf);
                    for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
                    return buf;
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