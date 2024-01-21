Aplicación SQL
Esta es una simple aplicación SQL.

Estructura de Archivos
__init__.py: Hace que Python trate el directorio como si contuviera paquetes.
1. crud.py: Contiene las operaciones de Crear, Leer, Actualizar y Eliminar para la base de datos.
2. database.py: Configura y establece la conexión a la base de datos.
3. main.py: El punto de entrada de la aplicación.
4. models.py: Define los modelos de la base de datos.
5. schemas.py: Define los modelos Pydantic para la validación y serialización de datos.
6. Configuración
Para configurar la aplicación, sigue estos pasos:

Instala los paquetes requeridos.
Configura la conexión a la base de datos en database.py.
Define tus modelos en models.py y tus esquemas en schemas.py.
Implementa tus operaciones CRUD en crud.py.
Configura tu aplicación en main.py.
Ejecución de la Aplicación


my_super_project> uvicorn sql_app.main:app --reload


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

dependencias
pip install fastapi
pip install uvicorn
pip install pydantic
pip install pyodbc
pip install SQLAlchemy