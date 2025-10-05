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

## 🚀 Ejecución de la Aplicación

### **Método Recomendado (Scripts Automatizados):**

1. **Para desarrollo rápido (servidor simplificado):**
   ```powershell
   .\start-dev.ps1
   ```

2. **Para servidor completo (cuando las migraciones estén OK):**
   ```powershell
   .\start-main.ps1
   ```

### **Comandos Manuales:**

1. **Activar entorno virtual:**
   ```powershell
   & sql_app\env\Scripts\Activate.ps1
   ```

2. **Servidor de desarrollo (recomendado):**
   ```bash
   uvicorn main_simple:app --host 127.0.0.1 --port 8001 --reload --log-level info
   ```

3. **Servidor principal (completo):**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info
   ```

### **URLs de Acceso:**
- 🌐 **Principal:** http://localhost:8001/
- 🎨 **Editor Visual:** http://localhost:8001/editor-visual
- ⚙️ **Generador:** http://localhost:8001/generar/test
- 📚 **Documentación completa:** Ver `COMANDOS_UVICORN.md`


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