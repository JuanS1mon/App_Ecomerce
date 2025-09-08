# migraciones.py

# Imports de bibliotecas estándar
import json
import logging
import os
from datetime import datetime, timedelta
from io import BytesIO

# Imports de terceros
import pandas as pd
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status
)
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Date, MetaData, Table, cast, func, inspect, text
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

# Imports del proyecto
from sql_app.Services.Analisis.analisis import clean_data
from sql_app.Services.migracion.migracion import procesar_archivo
from sql_app.Services.security.auth_middleware import require_role_api
from sql_app.db.crud.tablas import get_tables
from sql_app.db.database import get_db
from sql_app.db.models.config.activityLog import ActivityLog
from sql_app.db.schemas.config.Usuarios import UserDB

ALLOWED_EXTENSIONS = {
    'EXCEL': [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ],
    'CSV': [
        "text/csv",
        "application/csv",
        "text/plain"  # Algunos navegadores envían CSV como text/plain
    ]
}


progress_storage = {}
# Agregamos una clase para manejar el estado de la migración
class MigracionProgress:
    def __init__(self):
        self.total_sheets = 0
        self.processed_sheets = 0
        self.current_sheet = ""
        self.status = "iniciando"
        self.errors = []
        self.progress_percentage = 0
        self.retry_count = 0
        self.max_retries = 3

    def update(self, sheet_name: str, status: str, error: str = None):
        self.current_sheet = sheet_name
        self.status = status
        if error:
            self.errors.append({"sheet": sheet_name, "error": error})
        if status == "completado":
            self.processed_sheets += 1
            self.progress_percentage = (self.processed_sheets / self.total_sheets) * 100

    def to_dict(self):
        """Convierte el objeto a un diccionario para serialización JSON"""
        return {
            "total_sheets": self.total_sheets,
            "processed_sheets": self.processed_sheets,
            "current_sheet": self.current_sheet,
            "status": self.status,
            "errors": self.errors,
            "progress_percentage": self.progress_percentage,
            "retry_count": self.retry_count
        }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def process_sheet_with_retry(sheet_data, sheet_name, timestamp, user_results_dir):
    """Procesa una hoja con sistema de reintentos"""
    
    try:
        # Convertir columnas datetime
        datetime_columns = sheet_data.select_dtypes(include=['datetime64[ns]', 'datetime']).columns
        for column in datetime_columns:
            sheet_data[column] = sheet_data[column].dt.strftime('%Y-%m-%d %H:%M:%S')

        return sheet_data
    except Exception as e:
        logging.error(f"Error procesando hoja {sheet_name}: {str(e)}")
        raise

# Funciones para procesar archivos en segundo plano
async def process_excel_file_in_background(
    temp_file_path: str,
    nombre_migracion: str,
    timestamp: str,
    user_results_dir: str, 
    db: Session,
    current_user,
    progress: MigracionProgress
):
    """
    Procesa un archivo Excel en segundo plano.
    """
    try:
        logging.info(f"Iniciando procesamiento de archivo Excel: {temp_file_path}")
        progress.status = "procesando"
        
        # Usar xlrd para Excel antiguos (.xls) o openpyxl para nuevos (.xlsx)
        if temp_file_path.endswith('.xls'):
            try:
                excel = pd.ExcelFile(temp_file_path, engine='xlrd')
            except Exception as e:
                logging.error(f"Error al leer archivo XLS: {str(e)}")
                progress.status = "error"
                progress.errors.append({"sheet": "todas", "error": f"Error al leer archivo XLS: {str(e)}"})
                return
        else:
            try:
                excel = pd.ExcelFile(temp_file_path, engine='openpyxl')
            except Exception as e:
                logging.error(f"Error al leer archivo XLSX: {str(e)}")
                progress.status = "error"
                progress.errors.append({"sheet": "todas", "error": f"Error al leer archivo XLSX: {str(e)}"})
                return

        # Contar las hojas para actualizar el progreso
        sheet_names = excel.sheet_names
        progress.total_sheets = len(sheet_names)
        logging.info(f"Encontradas {progress.total_sheets} hojas en el archivo Excel")
        
        for sheet_name in sheet_names:
            try:
                progress.update(sheet_name, "procesando")
                logging.info(f"Procesando hoja: {sheet_name}")
                
                # Leer la hoja
                df = excel.parse(sheet_name, header=0)
                
                # Eliminar filas completamente vacías
                df.dropna(how='all', inplace=True)
                
                # Si el dataframe está vacío después de eliminar filas vacías, saltamos
                if df.empty:
                    progress.update(sheet_name, "completado", "Hoja vacía")
                    continue
                
                # Eliminar columnas completamente vacías  
                df.dropna(axis=1, how='all', inplace=True)
                
                # Procesar la hoja con el sistema de reintentos
                df = await process_sheet_with_retry(df, sheet_name, timestamp, user_results_dir)
                
                # Convertir a JSON (asegurando que los datos datetime se convierten correctamente)
                json_path = os.path.join(user_results_dir, f"{sheet_name}_{timestamp}.json")
                
                # Convertir al formato JSON usando orient='records' para una lista de diccionarios
                df.to_json(json_path, orient='records', date_format='iso')
                
                # Nombre de la tabla en la base de datos
                table_name = f"migracion_{nombre_migracion}_{sheet_name}_{timestamp}"
                table_name = table_name.replace(" ", "_").replace("-", "_").lower()
                
                # Guardar el resultado de la migración
                result_filename = f"result_{sheet_name}_{timestamp}.json"
                result_path = os.path.join(user_results_dir, result_filename)
                
                # Procesar el archivo JSON
                procesar_archivo(json_path, result_path, db, current_user, table_name)
                
                progress.update(sheet_name, "completado")
                
            except Exception as e:
                error_msg = f"Error procesando hoja {sheet_name}: {str(e)}"
                logging.error(error_msg)
                progress.update(sheet_name, "error", error_msg)
                continue
                
        # Actualizar el estado final
        if progress.errors:
            progress.status = "completado con errores"
        else:
            progress.status = "completado"
            
        # Eliminar el archivo temporal
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logging.warning(f"No se pudo eliminar el archivo temporal {temp_file_path}: {str(e)}")
        
    except Exception as e:
        logging.error(f"Error en el proceso de migración: {str(e)}")
        progress.status = "error"
        progress.errors.append({"sheet": "general", "error": f"Error general: {str(e)}"})
        
    finally:
        logging.info(f"Proceso de migración completado con estado: {progress.status}")

# Configuración de logging
logging.basicConfig(
    filename='logs/migraciones.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Crear directorios si no existen
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="sql_app/static")


router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
    prefix="/migraciones",
    tags=["Migraciones"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/check_progress")
async def check_progress(
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Verifica el progreso de la migración del usuario actual"""
    try:
        # Obtener el nombre de usuario
        user_name = current_user.usuario
        
        if not user_name:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        user_progress = progress_storage.get(user_name, MigracionProgress())
        return JSONResponse(content=user_progress.to_dict())
    except Exception as e:
        logging.error(f"Error al verificar progreso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al verificar progreso: {str(e)}")

@router.get("/nueva_migracion")
async def migraciones_page(
    request: Request,
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Página para crear una nueva migración"""
    try:
        return templates.TemplateResponse(
            "html/migraciones/migraciones_nueva.html", 
            {"request": request, "user": current_user}
        )
    except Exception as e:
        logging.error(f"Error al cargar página nueva migración: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cargar la página")
@router.post("/upload")
async def upload_migracion_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Sube y procesa archivos de migración (Excel/CSV)"""
    try:
        # Obtener información del usuario
        user_id = current_user.codigo
        user_name = current_user.usuario
        
        if not user_id or not user_name:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        # Validar tamaño del archivo (50MB máximo)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 50MB)")
        
        # Validar extensión del archivo
        if not file.filename or not any(file.filename.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        progress = MigracionProgress()
        progress_storage[user_name] = progress
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Configuración inicial
        user_results_dir = os.path.join(RESULTS_DIR, user_name)
        os.makedirs(user_results_dir, exist_ok=True)
        form = await request.form()
        nombre_migracion = form.get('migration_name', 'default_name')
        
        # Sanitizar nombre de migración
        nombre_migracion = "".join(c for c in nombre_migracion if c.isalnum() or c in ['_', '-']).lower()
        
        # Verificar el tipo de archivo sin leer todo el contenido
        if file.content_type in ALLOWED_EXTENSIONS['EXCEL']:
            # Guardar temporalmente el archivo (evita cargarlo completamente en memoria)
            temp_file_path = os.path.join(user_results_dir, f"temp_{timestamp}_{file.filename}")
            
            # Leer y escribir por chunks para archivos grandes
            CHUNK_SIZE = 1024 * 1024  # 1MB por chunk
            try:
                with open(temp_file_path, 'wb') as f:
                    while chunk := await file.read(CHUNK_SIZE):
                        if not chunk:
                            break
                        f.write(chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")
            
            # Procesar Excel en segundo plano
            background_tasks.add_task(
                process_excel_file_in_background,
                temp_file_path,
                nombre_migracion,
                timestamp,
                user_results_dir,
                db,
                current_user,
                progress
            )
            
        elif file.content_type in ALLOWED_EXTENSIONS['CSV']:
            # Para CSV, leer con una estrategia diferente por chunks
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail="El archivo está vacío")
            
            # Procesar CSV en segundo plano
            try:
                result = await process_csv_file(
                    contents,
                    nombre_migracion,
                    user_results_dir,
                    current_user,
                    db,
                    background_tasks,
                    progress
                )
                return JSONResponse(content=result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error procesando CSV: {str(e)}")
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no soportado: {file.content_type}"
            )

        return JSONResponse(content={
            "message": "Archivo recibido. El procesamiento se realizará en segundo plano.",
            "result_url": "/migraciones/control_migraciones",
            "progress": progress.to_dict()
        })

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error en el proceso de migración: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
@router.get("/control_migraciones")
async def get_all_results(
    request: Request,
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Página de control y resultados de migraciones"""
    try:
        # Obtener el nombre de usuario
        user_name = current_user.usuario
        
        if not user_name:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        user_results_dir = os.path.join(RESULTS_DIR, user_name)
        
        # Verificar si existe el directorio de resultados
        if not os.path.exists(user_results_dir):
            return templates.TemplateResponse(
                "html/migraciones/migraciones_results.html",
                {
                    "request": request,
                    "user": current_user,
                    "message": "No se encontraron resultados para este usuario.",
                    "results": []
                }
            )

        # Obtener los archivos de resultados y ordenarlos por fecha de modificación (más reciente primero)
        try:
            result_files = sorted(
                [f for f in os.listdir(user_results_dir) if f.startswith("result_") and f.endswith(".json")],
                key=lambda x: os.path.getmtime(os.path.join(user_results_dir, x)),
                reverse=True
            )
        except Exception as e:
            logging.error(f"Error al listar archivos de resultados: {str(e)}")
            result_files = []

        results = []
        for result_file in result_files:
            try:
                result_path = os.path.join(user_results_dir, result_file)
                with open(result_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    # Agregar información adicional
                    result['filename'] = result_file
                    result['file_size'] = os.path.getsize(result_path)
                    result['modified_time'] = datetime.fromtimestamp(
                        os.path.getmtime(result_path)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    results.append(result)
            except Exception as e:
                logging.error(f"Error al leer archivo {result_file}: {str(e)}")
                continue

        # Obtener progreso actual
        user_progress = progress_storage.get(user_name, MigracionProgress())

        return templates.TemplateResponse(
            "html/migraciones/migraciones_results.html",
            {
                "request": request,
                "user": current_user,
                "results": results,
                "progress": user_progress.to_dict()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error al obtener los resultados: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
@router.get("/admin_migraciones")
async def admin_migraciones_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Página principal de administración de migraciones con estadísticas y tablas"""
    try:
        # Obtener el ID del usuario
        user_id = current_user.codigo
        user_name = current_user.usuario
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        # Obtener las últimas actividades del usuario relacionadas con migraciones
        try:
            actividades = db.query(ActivityLog).filter(
                ActivityLog.user_id == user_id,  # Usar user_id consistentemente
                ActivityLog.action.ilike('%migración%')
            ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
        except Exception as e:
            logging.warning(f"Error al obtener actividades: {str(e)}")
            actividades = []

        # Contar el número total de migraciones realizadas por el usuario
        try:
            total_migraciones = db.query(ActivityLog).filter(
                ActivityLog.user_id == user_id,
                ActivityLog.action.ilike('%migración%')
            ).count()
        except Exception as e:
            logging.warning(f"Error al contar migraciones: {str(e)}")
            total_migraciones = 0

        # Preparar datos para el gráfico (migraciones por día)
        try:
            fecha_column = cast(ActivityLog.timestamp, Date)
            migraciones_por_dia = db.query(
                fecha_column.label('fecha'),
                func.count().label('cantidad')
            ).filter(
                ActivityLog.user_id == user_id,
                ActivityLog.action.ilike('%migración%')
            ).group_by(
                fecha_column
            ).order_by(
                fecha_column
            ).limit(30).all()  # Limitar a últimos 30 días
        except Exception as e:
            logging.warning(f"Error al obtener datos del gráfico: {str(e)}")
            migraciones_por_dia = []

        labels = [str(record.fecha) for record in migraciones_por_dia]
        data = [record.cantidad for record in migraciones_por_dia]

        # Obtener los nombres de las tablas
        try:
            tables1, tables2 = get_tables(db)
        except Exception as e:
            logging.error(f"Error al obtener tablas: {str(e)}")
            tables1, tables2 = [], []

        # Obtener progreso actual del usuario
        user_progress = progress_storage.get(user_name, MigracionProgress())

        # Renderizar la plantilla
        return templates.TemplateResponse(
            "html/migraciones/migraciones_admin.html",
            {
                "request": request,
                "user": current_user,
                "actividades": [actividad.action for actividad in actividades],
                "labels": labels,
                "data": data,
                "total_migraciones": total_migraciones,
                "tables1": tables1,
                "tables2": tables2,
                "progress": user_progress.to_dict()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error al cargar página de administración: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/tablas_migraciones")
async def migraciones_tablas(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Página para visualizar y gestionar tablas de migraciones"""
    try:
        tables1, tables2 = get_tables(db)
        
        # Obtener información adicional sobre las tablas
        inspector = inspect(db.get_bind())
        tables_info = []
        
        for table_name in tables1 + tables2:
            try:
                columns = inspector.get_columns(table_name)
                row_count_result = db.execute(text(f"SELECT COUNT(*) FROM [{table_name}]")).scalar()
                
                tables_info.append({
                    'name': table_name,
                    'column_count': len(columns),
                    'row_count': row_count_result or 0,
                    'is_migration_table': table_name.startswith('migracion_')
                })
            except Exception as e:
                logging.warning(f"Error al obtener info de tabla {table_name}: {str(e)}")
                tables_info.append({
                    'name': table_name,
                    'column_count': 0,
                    'row_count': 0,
                    'is_migration_table': table_name.startswith('migracion_'),
                    'error': str(e)
                })

        return templates.TemplateResponse(
            "html/migraciones/migraciones_tablas.html",
            {
                "request": request,
                "user": current_user,
                "tables1": tables1,
                "tables2": tables2,
                "tables_info": tables_info
            }
        )
    except Exception as e:
        error_msg = f"Error al cargar tablas: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/get_table_fields/{table_name}")
async def get_table_fields(
    table_name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Obtiene los campos de una tabla específica"""
    try:
        # Validar nombre de tabla
        if not table_name or not table_name.replace('_', '').replace('-', '').isalnum():
            raise HTTPException(status_code=400, detail="Nombre de tabla no válido")
        
        # Obtener los nombres de las columnas y sus tipos de datos
        inspector = inspect(db.get_bind())
        
        # Verificar que la tabla existe
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"La tabla '{table_name}' no existe")
        
        columns = inspector.get_columns(table_name)
        fields = [
            {
                "name": column["name"], 
                "type": str(column["type"]),
                "nullable": column.get("nullable", True),
                "default": column.get("default", None)
            } 
            for column in columns
        ]

        return {"fields": fields, "table_name": table_name}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error al obtener campos de la tabla: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/get_table_records/{table_name}")
async def get_table_records(
    table_name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    # Asegurarse de que el nombre de la tabla es una cadena
    if isinstance(table_name, list):
        table_name = table_name[0]

    # Obtener los primeros 5 registros de la tabla
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=db.get_bind())
    #query = db.query(table).limit(5).all()
    query = db.query(table).all()
    records = [dict(row._mapping) for row in query]

    return {"records": records}



@router.post("/migrate_data")
async def migrate_data(
    migration_data: dict,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    source_table_name = migration_data.get('source_table')
    target_table_name = migration_data.get('target_table')
    mappings = migration_data.get('mappings')  # Lista de diccionarios con "from" y "to"

    if not source_table_name or not target_table_name or not mappings:
        raise HTTPException(status_code=400, detail="Datos de migración incompletos.")

    try:
        # Asegurarse de que los nombres de las tablas son cadenas
        if isinstance(source_table_name, list):
            source_table_name = source_table_name[0]
        if isinstance(target_table_name, list):
            target_table_name = target_table_name[0]

        # Cargar las tablas reflejadas
        metadata = MetaData()
        source_table = Table(source_table_name, metadata, autoload_with=db.get_bind())
        target_table = Table(target_table_name, metadata, autoload_with=db.get_bind())

        # Obtener todos los registros de la tabla de origen
        source_query = db.query(source_table).all()
        source_data = [dict(row._mapping) for row in source_query]

        # Preparar los datos para insertar en la tabla de destino
        target_data = []
        for row in source_data:
            new_row = {}
            for mapping in mappings:
                source_field = mapping['from']
                target_field = mapping['to']
                if source_field in row:
                    new_row[target_field] = row[source_field]
            if new_row:
                target_data.append(new_row)

        # Limpiar datos duplicados
        target_data = clean_data(target_data)

        # Insertar los datos en la tabla de destino
        db.execute(target_table.insert(), target_data)
        db.commit()

        return {"message": "Migración completada exitosamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al migrar datos: {str(e)}")
    
# Función para procesar archivos CSV
async def process_csv_file(
    contents: bytes,
    nombre_migracion: str,
    user_results_dir: str,
    current_user: UserDB,
    db: Session,
    background_tasks: BackgroundTasks,
    progress: MigracionProgress
) -> dict:
    try:
        # Leer el archivo CSV
        df = pd.read_csv(
            BytesIO(contents),
            sep=",",
            quotechar='"',
            encoding="utf-8-sig",
            engine="python",
            on_bad_lines='skip'  # o 'warn' para mostrar advertencias
        )
        # Verificar nombres de columnas para depuración
        column_names = list(df.columns)
        logging.info(f"Columnas leídas del CSV: {column_names}")

        progress.total_sheets = 1
        progress.update("csv_data", "procesando")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        table_name = f"migracion_{nombre_migracion}_csv_{timestamp}"
        
        # Convertir a JSON
        json_path = os.path.join(user_results_dir, f"datos_csv_{timestamp}.json")
        df.to_json(json_path, orient='records', date_format='iso')

        # Configurar tarea en segundo plano
        result_filename = f"result_csv_{timestamp}.json"
        result_path = os.path.join(user_results_dir, result_filename)
        
        background_tasks.add_task(
            procesar_archivo,
            json_path,
            result_path,
            db,
            current_user,
            table_name
        )

        progress.update("csv_data", "completado")
        return {
            "status": "success",
            "message": "Archivo CSV procesado correctamente",
            "progress": progress.to_dict()
        }
    except Exception as e:
        error_msg = f"Error procesando CSV: {str(e)}"
        progress.update("csv_data", "error", error_msg)
        logging.error(error_msg)
        raise
    

# Crear un modelo para la solicitud de renombrar tabla
class RenameTableRequest(BaseModel):
    current_name: str
    new_name: str
@router.post("/rename_table")
async def rename_table(
    request: RenameTableRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    try:
        # Verificar que la tabla actual existe
        inspector = inspect(db.get_bind())
        if request.current_name not in inspector.get_table_names():
            return JSONResponse(
                content={"success": False, "message": f"La tabla '{request.current_name}' no existe"},
                status_code=400
            )
        
        # Verificar que el nuevo nombre no existe
        if request.new_name in inspector.get_table_names():
            return JSONResponse(
                content={"success": False, "message": f"Ya existe una tabla con el nombre '{request.new_name}'"},
                status_code=400
            )
        
        # Cerrar la sesión actual para liberar cualquier conexión activa
        db.close()
        
        # Crear una nueva conexión para ejecutar el SQL directamente
        engine = db.get_bind()
        
        # Ejecutar SQL para renombrar la tabla - usar la sintaxis correcta para SQL Server
        with engine.begin() as conn:
            # SQL Server usa sp_rename para renombrar tablas
            conn.execute(text(f"EXEC sp_rename '{request.current_name}', '{request.new_name}'"))
        
        # Registrar la actividad
        log_entry = ActivityLog(
            user_id=current_user.codigo,
            action=f"Renombró tabla de '{request.current_name}' a '{request.new_name}'",
            timestamp=datetime.now()
        )
        db.add(log_entry)
        db.commit()
        
        return JSONResponse(
            content={"success": True, "message": f"Tabla renombrada exitosamente a '{request.new_name}'"}
        )
        
    except Exception as e:
        db.rollback()
        error_msg = f"Error al renombrar la tabla: {str(e)}"
        logging.error(error_msg)
        
        return JSONResponse(
            content={"success": False, "message": error_msg},
            status_code=500
        )

class ChangeFieldTypeRequest(BaseModel):
    table_name: str
    field_name: str
    current_type: str
    new_type: str

@router.post("/change_field_type")
async def change_field_type(
    request: ChangeFieldTypeRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Cambia el tipo de un campo en una tabla con validaciones y manejo seguro de conversiones."""
    try:
        # 1. Verificaciones iniciales
        inspector = inspect(db.get_bind())
        
        # Verificar existencia de tabla y campo
        if request.table_name not in inspector.get_table_names():
            return JSONResponse(
                content={"success": False, "message": f"La tabla '{request.table_name}' no existe"},
                status_code=400
            )
        
        columns = inspector.get_columns(request.table_name)
        if not any(col["name"] == request.field_name for col in columns):
            return JSONResponse(
                content={"success": False, "message": f"El campo '{request.field_name}' no existe en la tabla '{request.table_name}'"},
                status_code=400
            )
        
        # Validar conversión de tipos permitida
        if request.current_type == 'VARCHAR' and request.new_type == 'INT':
            return JSONResponse(
                content={"success": False, "message": "No se puede convertir VARCHAR a INT"},
                status_code=400
            )
        
        # Mapeo de tipos de datos simplificado
        type_mapping = {'VARCHAR': 'VARCHAR(255)', 'INT': 'INT', 'DATE': 'DATE'}
        sql_type = type_mapping.get(request.new_type, 'VARCHAR(255)')
        
        # 2. Manejo específico para conversión a DATE
        if request.new_type == 'DATE':
            return await _handle_date_conversion(request, db, current_user)
        
        # 3. Manejo para otros tipos de conversión
        db.close()  # Cerrar la sesión antes de operaciones ALTER TABLE
        
        with db.get_bind().begin() as conn:
            conn.execute(text(f"ALTER TABLE [{request.table_name}] ALTER COLUMN [{request.field_name}] {sql_type}"))
        
        # Registrar la actividad
        log_entry = ActivityLog(
            user_id=current_user.codigo,
            action=f"Cambió el tipo de campo '{request.field_name}' en la tabla '{request.table_name}' de '{request.current_type}' a '{request.new_type}'",
            timestamp=datetime.now()
        )
        db.add(log_entry)
        db.commit()
        
        return JSONResponse(
            content={"success": True, "message": f"Tipo de campo actualizado correctamente a '{request.new_type}'"}
        )
        
    except Exception as e:
        db.rollback()
        error_msg = f"Error al cambiar el tipo de campo: {str(e)}"
        logging.error(error_msg)
        
        # Mejorar mensaje para error de conversión de fechas
        if "convertir una cadena de caracteres en fecha" in str(e):
            return JSONResponse(
                content={
                    "success": False, 
                    "message": "La columna contiene valores que no son fechas válidas. "
                              "Formatos aceptados: 'YYYY-MM-DD', 'YYYY/MM/DD', 'DD-MM-YYYY', etc. "
                              "Se recomienda limpiar los datos antes de cambiar el tipo."
                },
                            status_code=400
            )
        
        return JSONResponse(
            content={"success": False, "message": error_msg},
            status_code=500
        )


async def _handle_date_conversion(request: ChangeFieldTypeRequest, db: Session, current_user):
    """Función auxiliar para manejar específicamente la conversión a tipo DATE con limpieza de datos."""
    try:
        # Obtener el ID del usuario
        user_id = current_user.codigo
        
        # Primero cerramos la sesión existente para evitar conflictos
        db.close()
        
        # Usamos una transacción explícita con begin() para garantizar que todo se ejecute o nada
        with db.get_bind().begin() as conn:
            # El resto del código de conversión permanece igual...
            
            # Verificar si la columna temporal existe y eliminarla si es el caso
            conn.execute(text(f"""
                IF EXISTS (
                    SELECT 1 FROM sys.columns 
                    WHERE object_id = OBJECT_ID('{request.table_name}') 
                    AND name = '{request.field_name}_temp'
                )
                BEGIN
                    ALTER TABLE [{request.table_name}] DROP COLUMN [{request.field_name}_temp]
                END
            """))
            
            # Obtener el tipo de datos de la columna
            column_info = conn.execute(text(f"""
                SELECT DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{request.table_name}' 
                AND COLUMN_NAME = '{request.field_name}'
            """)).scalar()
            
            is_numeric = column_info in ('bigint', 'int', 'smallint', 'tinyint', 'numeric', 'decimal')
            
            # Crear la columna temporal
            conn.execute(text(f"ALTER TABLE [{request.table_name}] ADD [{request.field_name}_temp] DATE NULL"))
            
            if is_numeric:
                # Para campos numéricos, convertimos directamente a fecha
                conn.execute(text(f"""
                    UPDATE [{request.table_name}]
                    SET [{request.field_name}_temp] = 
                        CASE 
                            -- Si es un año de 4 dígitos
                            WHEN [{request.field_name}] BETWEEN 1000 AND 9999
                                THEN DATEFROMPARTS([{request.field_name}], 1, 1)
                            
                            -- Si es un año de 2 dígitos
                            WHEN [{request.field_name}] BETWEEN 0 AND 99
                                THEN DATEFROMPARTS(
                                    CASE WHEN [{request.field_name}] > 50 THEN 1900 ELSE 2000 END + [{request.field_name}], 
                                    1, 1)
                            
                            -- Otros valores numéricos no se pueden convertir
                            ELSE NULL
                        END
                    WHERE [{request.field_name}] IS NOT NULL
                """))
            else:
                # Para campos de texto, realizamos limpieza y conversión
                # Similar al código existente...
                
                # 3. Intentar conversión directa a fecha con TRY_CONVERT
                conn.execute(text(f"""
                    UPDATE [{request.table_name}] 
                    SET [{request.field_name}_temp] = TRY_CONVERT(DATE, [{request.field_name}])
                    WHERE [{request.field_name}] IS NOT NULL
                """))
                
                # 4. Intentar conversión para formatos específicos donde TRY_CONVERT falló
                conn.execute(text(f"""
                    UPDATE t
                    SET t.[{request.field_name}_temp] = 
                        CASE 
                            -- Formato DD-MM-YYYY a YYYY-MM-DD
                            WHEN LEN(t.[{request.field_name}]) = 10 
                                AND SUBSTRING(t.[{request.field_name}], 3, 1) = '-' 
                                AND SUBSTRING(t.[{request.field_name}], 6, 1) = '-'
                            THEN TRY_CONVERT(DATE, 
                                SUBSTRING(t.[{request.field_name}], 7, 4) + '-' + 
                                SUBSTRING(t.[{request.field_name}], 4, 2) + '-' + 
                                SUBSTRING(t.[{request.field_name}], 1, 2))
                                
                            -- Formato DD/MM/YYYY a YYYY-MM-DD
                            WHEN LEN(t.[{request.field_name}]) = 10 
                                AND SUBSTRING(t.[{request.field_name}], 3, 1) = '/' 
                                AND SUBSTRING(t.[{request.field_name}], 6, 1) = '/'
                            THEN TRY_CONVERT(DATE,
                                SUBSTRING(t.[{request.field_name}], 7, 4) + '-' + 
                                SUBSTRING(t.[{request.field_name}], 4, 2) + '-' + 
                                SUBSTRING(t.[{request.field_name}], 1, 2))
                                
                            ELSE t.[{request.field_name}_temp]
                        END
                    FROM [{request.table_name}] t
                    WHERE t.[{request.field_name}] IS NOT NULL 
                    AND t.[{request.field_name}_temp] IS NULL
                """))
            
            # El resto del código de conversión permanece igual...
        
        # La transacción se ha completado exitosamente, ahora podemos registrar la actividad
        # Crear una nueva sesión para el registro
        log_entry = ActivityLog(
            user_id=user_id,  # Usar user_id consistentemente
            action=f"Cambió el tipo de campo '{request.field_name}' en la tabla '{request.table_name}' de '{request.current_type}' a 'DATE'",
            timestamp=datetime.now()
        )
        db.add(log_entry)
        db.commit()
        
        return JSONResponse(
            content={"success": True, "message": f"Tipo de campo actualizado correctamente a DATE"}
        )
    except Exception as e:
        # Asegurarse de que se revierta la transacción
        db.rollback()
        error_msg = f"Error durante la conversión a DATE: {str(e)}"
        logging.error(error_msg)
        
        return JSONResponse(
            content={"success": False, "message": error_msg},
            status_code=500
        )
    
async def process_excel_file_in_background(
    file_path: str,
    nombre_migracion: str,
    timestamp: str,
    user_results_dir: str,
    db: Session,
    current_user: UserDB,
    progress: MigracionProgress
):
    try:
        # Determinar el motor Excel adecuado según la extensión del archivo
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.xls':
            excel_engine = 'xlrd'  # Motor para archivos .xls
        else:
            excel_engine = 'openpyxl'  # Motor para archivos .xlsx
            
        # Usar ExcelFile para leer las hojas bajo demanda
        with pd.ExcelFile(file_path, engine=excel_engine) as xls:
            sheet_names = xls.sheet_names
            progress.total_sheets = len(sheet_names)
            
            # Procesar cada hoja individualmente
            for sheet_name in sheet_names:
                progress.update(sheet_name, "procesando")
                table_name = f"migracion_{nombre_migracion}_{sheet_name}_{timestamp}"
                
                try:
                    # Leer solo esta hoja y liberar memoria después
                    df = pd.read_excel(
                        file_path, 
                        sheet_name=sheet_name, 
                        engine=excel_engine, 
                        # Optimizaciones para archivos grandes
                        dtype='object',  # Usa tipos inferidos más tarde en smaller chunks
                        na_filter=False,  # Desactivar el filtro NA para aumentar velocidad
                    )
                    
                    # Convertir columnas datetime de manera más eficiente
                    datetime_columns = df.select_dtypes(include=['datetime64[ns]', 'datetime']).columns
                    for column in datetime_columns:
                        df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Guardar directamente a JSON en disco
                    sheet_json_path = os.path.join(user_results_dir, f"{sheet_name}_datos.json")
                    
                    # Dividir el DataFrame en chunks para procesar archivos grandes
                    ROWS_PER_CHUNK = 10000
                    total_rows = len(df)
                    
                    # Si es un archivo pequeño, procesarlo directamente
                    if total_rows <= ROWS_PER_CHUNK:
                        df.to_json(sheet_json_path, orient='records', date_format='iso')
                        
                        # Limpiar formato de fechas (procesar archivo JSON ya generado)
                        with open(sheet_json_path, 'r', encoding='utf-8') as f:
                            sample_data = json.load(f)
                            for record in sample_data:
                                for key, value in record.items():
                                    if isinstance(value, str) and 'T' in value:
                                        record[key] = value.replace('T', ' ').split('.')[0]
                                        
                        with open(sheet_json_path, 'w', encoding='utf-8') as f:
                            json.dump(sample_data, f, ensure_ascii=False, indent=4)
                    else:
                        # Para archivos grandes, procesar por chunks
                        with open(sheet_json_path, 'w', encoding='utf-8') as f:
                            # Escribir inicio del array JSON
                            f.write('[\n')
                            
                            for chunk_start in range(0, total_rows, ROWS_PER_CHUNK):
                                chunk_end = min(chunk_start + ROWS_PER_CHUNK, total_rows)
                                chunk = df.iloc[chunk_start:chunk_end]
                                
                                # Convertir chunk a JSON y limpiar
                                chunk_json = chunk.to_json(orient='records', date_format='iso')
                                chunk_data = json.loads(chunk_json)
                                
                                # Limpiar formato de fechas
                                for record in chunk_data:
                                    for key, value in record.items():
                                        if isinstance(value, str) and 'T' in value:
                                            record[key] = value.replace('T', ' ').split('.')[0]
                                
                                # Escribir cada registro con formato apropiado
                                for i, record in enumerate(chunk_data):
                                    json_str = json.dumps(record, ensure_ascii=False)
                                    # Añadir coma si no es el último chunk y no es el último registro
                                    if chunk_end < total_rows or i < len(chunk_data) - 1:
                                        f.write(f"  {json_str},\n")
                                    else:
                                        f.write(f"  {json_str}\n")
                            
                            # Cerrar el array JSON
                            f.write(']')
                    
                    # Configurar tarea de procesamiento para este JSON
                    result_filename = f"result_{sheet_name}_{timestamp}.json"
                    result_path = os.path.join(user_results_dir, result_filename)
                    
                    # Aquí usamos run_in_threadpool para no bloquear mientras se procesa
                    from fastapi.concurrency import run_in_threadpool
                    await run_in_threadpool(
                        procesar_archivo,
                        sheet_json_path,
                        result_path,
                        db,
                        current_user,
                        table_name
                    )
                    
                    progress.update(sheet_name, "completado")
                    
                    # Limpiar memoria explícitamente
                    del df
                    import gc
                    gc.collect()
                    
                except Exception as e:
                    error_msg = f"Error en hoja {sheet_name}: {str(e)}"
                    progress.update(sheet_name, "error", error_msg)
                    logging.error(error_msg)
                    continue
            
        # Eliminar archivo temporal
        os.remove(file_path)
        
    except Exception as e:
        error_msg = f"Error procesando archivo Excel: {str(e)}"
        logging.error(error_msg)
        progress.status = "error"
        progress.errors.append({"sheet": "general", "error": error_msg})

# Agregar ruta principal para breadcrumb
@router.get("/")
async def migraciones_index(
    request: Request,
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Página índice de migraciones - redirige a admin_migraciones"""
    return RedirectResponse(url="/migraciones/admin_migraciones", status_code=302)

# Agregar endpoint para estadísticas de migraciones
@router.get("/api/stats")
async def get_migration_stats(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """API para obtener estadísticas de migraciones"""
    try:
        user_id = current_user.codigo
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        # Estadísticas básicas
        total_migrations = db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.action.ilike('%migración%')
        ).count()
        
        # Migraciones por mes
        monthly_migrations = db.query(
            func.strftime('%Y-%m', ActivityLog.timestamp).label('month'),
            func.count().label('count')
        ).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.action.ilike('%migración%')
        ).group_by(
            func.strftime('%Y-%m', ActivityLog.timestamp)
        ).order_by('month').all()
        
        # Tablas de migración existentes
        inspector = inspect(db.get_bind())
        migration_tables = [
            table for table in inspector.get_table_names() 
            if table.startswith('migracion_')
        ]
        
        return {
            "total_migrations": total_migrations,
            "monthly_data": [{"month": m.month, "count": m.count} for m in monthly_migrations],
            "migration_tables_count": len(migration_tables),
            "migration_tables": migration_tables[:10]  # Últimas 10 tablas
        }
    except Exception as e:
        logging.error(f"Error al obtener estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# Endpoint para limpiar archivos temporales antiguos
@router.delete("/api/cleanup")
async def cleanup_old_files(
    days: int = 30,
    current_user: UserDB = Depends(require_role_api(["admin"]))
):
    """Limpia archivos temporales y de resultados antiguos"""
    try:
        user_name = current_user.usuario
        
        if not user_name:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        user_results_dir = os.path.join(RESULTS_DIR, user_name)
        
        if not os.path.exists(user_results_dir):
            return {"message": "No hay archivos para limpiar", "files_deleted": 0}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        files_deleted = 0
        
        for filename in os.listdir(user_results_dir):
            file_path = os.path.join(user_results_dir, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_modified < cutoff_date and (filename.startswith('temp_') or filename.startswith('result_')):
                try:
                    os.remove(file_path)
                    files_deleted += 1
                    logging.info(f"Archivo eliminado: {filename}")
                except Exception as e:
                    logging.warning(f"No se pudo eliminar {filename}: {str(e)}")
        
        return {
            "message": f"Limpieza completada. Archivos más antiguos que {days} días eliminados.",
            "files_deleted": files_deleted
        }
    except Exception as e:
        logging.error(f"Error en limpieza: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")