# migraciones.py
from io import BytesIO
import os
import logging
from fastapi import APIRouter, Request, status, Depends, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from Services.migracion.migracion import procesar_archivo
from Services.security.security import get_current_user
from db.database import get_db
from db.schemas.Maestro.Usuarios import UserDB
from datetime import datetime
import json
from sqlalchemy.orm import Session
from db.crud.tablas import get_tables
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi.responses import JSONResponse

from Services.Analisis.analisis import clean_data


from sqlalchemy import inspect, Table, MetaData, func, cast, Date

from db.models.activityLog import ActivityLog




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
templates = Jinja2Templates(directory="static/html")


router = APIRouter(
    prefix="/migraciones",
    tags=["Migraciones"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/check_progress")
async def check_progress(
    current_user: UserDB = Depends(get_current_user)
):
    user_progress = progress_storage.get(current_user.usuario, MigracionProgress())
    return JSONResponse(content=user_progress.to_dict())

@router.get("/nueva_migracion")
async def migraciones_page(
    request: Request,
    current_user: UserDB = Depends(get_current_user)
):
    return templates.TemplateResponse("migraciones_nueva.html", {"request": request, "user": current_user})


@router.post("/upload")
async def upload_migracion_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    progress = MigracionProgress()
    progress_storage[current_user.usuario] = progress
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Agregar esta línea
    
    try:
        contents = await file.read()
        if not contents:
            return JSONResponse(
                content={
                    "error": "El archivo está vacío.",
                    "progress": progress.to_dict()
                },
                status_code=400
            )

        # Configuración inicial
        user_results_dir = os.path.join(RESULTS_DIR, current_user.usuario)
        os.makedirs(user_results_dir, exist_ok=True)
        form = await request.form()
        nombre_migracion = form.get('migration_name', 'default_name')
        
        # Detectar tipo de archivo y procesar
        if file.content_type in ALLOWED_EXTENSIONS['EXCEL']:
            # Procesar Excel
            excel_data = pd.read_excel(BytesIO(contents), sheet_name=None)
            progress.total_sheets = len(excel_data)

            for sheet_name, sheet_data in excel_data.items():
                progress.update(sheet_name, "procesando")
                table_name = f"migracion_{nombre_migracion}_{sheet_name}_{timestamp}"

                try:
                    processed_data = await process_sheet_with_retry(
                        sheet_data, sheet_name, timestamp, user_results_dir
                    )

                    sheet_json_path = os.path.join(user_results_dir, f"{sheet_name}_datos.json")
                    processed_data.to_json(sheet_json_path, orient='records', date_format='iso')

                    with open(sheet_json_path, 'r', encoding='utf-8') as f:
                        sample_data = json.load(f)
                        for record in sample_data:
                            for key, value in record.items():
                                if isinstance(value, str) and 'T' in value:
                                    record[key] = value.replace('T', ' ').split('.')[0]

                    with open(sheet_json_path, 'w', encoding='utf-8') as f:
                        json.dump(sample_data, f, ensure_ascii=False, indent=4)

                    result_filename = f"result_{sheet_name}_{timestamp}.json"
                    result_path = os.path.join(user_results_dir, result_filename)
                    background_tasks.add_task(
                        procesar_archivo,
                        sheet_json_path,
                        result_path,
                        db,
                        current_user,
                        table_name
                    )

                    progress.update(sheet_name, "completado")

                except Exception as e:
                    error_msg = f"Error en hoja {sheet_name}: {str(e)}"
                    progress.update(sheet_name, "error", error_msg)
                    logging.error(error_msg)
                    continue

        elif file.content_type in ALLOWED_EXTENSIONS['CSV']:
            # Procesar CSV
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
                return JSONResponse(
                    content={
                        "error": f"Error procesando CSV: {str(e)}",
                        "progress": progress.to_dict()
                    },
                    status_code=500
                )

        else:
            return JSONResponse(
                content={
                    "error": f"Tipo de archivo no soportado: {file.content_type}",
                    "progress": progress.to_dict()
                },
                status_code=400
            )

        return JSONResponse(content={
            "message": "Archivo recibido. El procesamiento se realizará en segundo plano.",
            "result_url": "/migraciones/control_migraciones",
            "progress": progress.to_dict()
        })

    except Exception as e:
        error_msg = f"Error en el proceso de migración: {str(e)}"
        logging.error(error_msg)
        return JSONResponse(
            content={
                "error": error_msg,
                "progress": progress.to_dict()
            },
            status_code=500
        )
    
@router.get("/control_migraciones")
async def get_all_results(
    request: Request,
    current_user: UserDB = Depends(get_current_user)
):
    try:
        user_results_dir = os.path.join(RESULTS_DIR, current_user.usuario)
        if not os.path.exists(user_results_dir):
            return templates.TemplateResponse(
                "migraciones_results.html",
                {
                    "request": request,
                    "message": "No se encontraron resultados para este usuario."
                }
            )

        # Obtener los archivos de resultados y ordenarlos por fecha de modificación (más reciente primero)
        result_files = sorted(
            [f for f in os.listdir(user_results_dir) if f.startswith("result_") and f.endswith(".json")],
            key=lambda x: os.path.getmtime(os.path.join(user_results_dir, x)),
            reverse=True
        )

        results = []
        for result_file in result_files:
            result_path = os.path.join(user_results_dir, result_file)
            with open(result_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
                results.append(result)

        return templates.TemplateResponse(
            "migraciones_results.html",
            {
                "request": request,
                "results": results
            }
        )
    except Exception as e:
        logging.error(f"Error al obtener los resultados: {str(e)}")
        return templates.TemplateResponse(
            "migraciones_results.html",
            {
                "request": request,
                "error": f"Error al obtener los resultados: {str(e)}"
            }
        )
    
@router.get("/admin_migraciones")
async def admin_migraciones_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
    ):
        # Obtener las últimas actividades del usuario relacionadas con migraciones
        actividades = db.query(ActivityLog).filter(
            ActivityLog.usuario_id == current_user.codigo,
            ActivityLog.action.ilike('%migración%')
        ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
        # Contar el número total de migraciones realizadas por el usuario
        total_migraciones = db.query(ActivityLog).filter(
            ActivityLog.usuario_id == current_user.codigo,
            ActivityLog.action.ilike('%migración%')
        ).count()
    
        # Preparar datos para el gráfico (migraciones por día)
        fecha_column = cast(ActivityLog.timestamp, Date)
    
        migraciones_por_dia = db.query(
            fecha_column.label('fecha'),
            func.count().label('cantidad')
        ).filter(
            ActivityLog.usuario_id == current_user.codigo,
            ActivityLog.action.ilike('%migración%')
        ).group_by(
            fecha_column
        ).order_by(
            fecha_column
        ).all()
    
        labels = [str(record.fecha) for record in migraciones_por_dia]
        data = [record.cantidad for record in migraciones_por_dia]
    
        # Obtener los nombres de las tablas
        tables1, tables2 = get_tables(db)
    
        # Log las tablas obtenidas
        logging.info(f"Tables1: {tables1}")
    
        # Renderizar la plantilla
        return templates.TemplateResponse(
            "migraciones_admin.html",
            {
                "request": request,
                "user": current_user,
                "actividades": [actividad.action for actividad in actividades],
                "labels": labels,
                "data": data,
                "total_migraciones": total_migraciones,
                "tables1": tables1,
                "tables2": tables2
            }
        )


@router.get("/tablas_migraciones")
async def migraciones_tablas(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    tables1, tables2 = get_tables(db)

    return templates.TemplateResponse(
        "migraciones_tablas.html",
        {
            "request": request,
            "user": current_user,
            "tables1": tables1,
            "tables2": tables2
        }
    )

@router.get("/get_table_fields/{table_name}")
async def get_table_fields(
    table_name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # Obtener los nombres de las columnas y sus tipos de datos
    inspector = inspect(db.get_bind())
    columns = inspector.get_columns(table_name)
    fields = [{"name": column["name"], "type": str(column["type"])} for column in columns]

    return {"fields": fields}

@router.get("/get_table_records/{table_name}")
async def get_table_records(
    table_name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
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
    current_user: UserDB = Depends(get_current_user)
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
    
# Primero, definimos los tipos de archivo permitidos
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
        df = pd.read_csv(BytesIO(contents))
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
    

 