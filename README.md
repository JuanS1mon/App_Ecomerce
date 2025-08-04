Aplicación SQL
Esta es una simple aplicación SQL.

Estructura de Archivos
__init__.py: Hace que Python trate el directorio como si contuviera paquetes.
1. crud.py: Contiene las operaciones de Crear, Leer, Actualizar y Eliminar para la base de datos.
2. database.py: Configura y establece la conexión a la base de datos.
3. main.py: El punto de entrada de la aplicación.
4. models.py: Define los modelos de la base de datos.
5. schemas.py: Define los modelos Pydantic para la validación y serialización de datos.

## Configuración

Para configurar la aplicación, sigue estos pasos:

1. Instala los paquetes requeridos con `pip install -r requirements.txt`.
2. Configura la conexión a la base de datos en `database.py`.
3. Define tus modelos en `models.py` y tus esquemas en `schemas.py`.
4. Implementa tus operaciones CRUD en `crud.py`.
5. Configura tu aplicación en `main.py`.

## Ejecución de la Aplicación

Para ejecutar la aplicación, navega a la carpeta del proyecto y ejecuta el siguiente comando:

```sh
uvicorn main:app --reload


ESTRUCTURA de carpetas. 
/my_super_proyect
    /env (Entorno virtual)
    /sql_app
        __init__.py
        crud.py
        database.py
        main.py
        models.py
        schemas.py
    README.md

Dependencias
Este proyecto utiliza las siguientes dependencias:

pip install -r requerimientos.txt
pip install fastapi
pip install uvicorn
pip install pydantic
pip install pyodbc
pip install SQLAlchemy
pip install python-multipart
pip install jinja2
pip install python-dotenv

para encriptacion web.
pip install python-jose[cryptography]
pip install passlib
pip install pycryptodome
pip install request
pip install pandas
pip install yattag
pip install beautifulsoup4
pip install openpyxl