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

from Services.Analisis.analisis import clean_data


from sqlalchemy import inspect, Table, MetaData, func, cast, Date

from db.models.activityLog import ActivityLog

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
    try:
        # Validaciones iniciales
        if file.content_type not in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]:
            logging.warning(f"Tipo de archivo inválido: {file.content_type}")
            return templates.TemplateResponse(
                "migraciones_nueva.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "Tipo de archivo inválido. Solo se aceptan archivos Excel (.xls, .xlsx)."
                }
            )

        # Leer archivo
        contents = await file.read()

        # Validar que el archivo no esté vacío
        if not contents:
            return templates.TemplateResponse(
                "migraciones_nueva.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "El archivo está vacío."
                }
            )

        # Crear directorio del usuario si no existe
        user_results_dir = os.path.join(RESULTS_DIR, current_user.usuario)
        os.makedirs(user_results_dir, exist_ok=True)

        # Obtener la fecha y hora actual
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Nombre de la migración (obtenido del request)
        form = await request.form()
        nombre_migracion = form.get('migration_name', 'default_name')

        # Leer el archivo Excel
        excel_data = pd.read_excel(BytesIO(contents), sheet_name=None)  # Leer todas las hojas

        # Procesar cada hoja
        for sheet_name, sheet_data in excel_data.items():            
            # Nombre de la tabla para cada hoja
            table_name = f"migracion_{nombre_migracion}_{sheet_name}_{timestamp}"

            # Convertir columnas de tipo datetime a cadenas de texto
            datetime_columns = sheet_data.select_dtypes(include=['datetime64[ns]', 'datetime']).columns
            for column in datetime_columns:
                try:
                    sheet_data[column] = sheet_data[column].dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    logging.error(f"Error al convertir la columna {column} a cadena de texto: {str(e)}")
                    sheet_data[column] = sheet_data[column].astype(str)

            # Verificación adicional: Asegurarse de que no queden columnas datetime
            remaining_datetime_columns = sheet_data.select_dtypes(include=['datetime64[ns]', 'datetime']).columns
            if len(remaining_datetime_columns) > 0:
                logging.warning(f"Quedan columnas datetime en la hoja {sheet_name}: {remaining_datetime_columns.tolist()}")
                for column in remaining_datetime_columns:
                    sheet_data[column] = sheet_data[column].astype(str)

            # Verificación de tipos después de la conversión
            for column in sheet_data.columns:
                if sheet_data[column].dtype == 'object':
                    sample_value = sheet_data[column].dropna().astype(str).iloc[0] if not sheet_data[column].dropna().empty else ''
                    logging.info(f"Columna '{column}' tipo object con ejemplo de valor: {sample_value}")

            # Ruta donde se guardará el archivo JSON para cada hoja
            sheet_json_path = os.path.join(user_results_dir, f"{sheet_name}_datos.json")
            sheet_data.to_json(sheet_json_path, orient='records', date_format='iso')  # Asegurar formato de fecha

            # Verificación del archivo JSON creado
            with open(sheet_json_path, 'r', encoding='utf-8') as f:
                try:
                    sample_data = json.load(f)
                    for record in sample_data:
                        for key, value in record.items():
                            if isinstance(value, str) and 'T' in value:  # Detectar formato ISO
                                adjusted_value = value.replace('T', ' ').split('.')[0]
                                record[key] = adjusted_value
                except json.JSONDecodeError as jde:
                    logging.error(f"Error al decodificar JSON para la hoja {sheet_name}: {str(jde)}")
                    continue  # Saltar a la siguiente hoja en caso de error

            # Guardar el JSON corregido
            with open(sheet_json_path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=4)

            # Ruta donde se guardará el resultado para cada hoja
            result_filename = f"result_{sheet_name}_{timestamp}.json"
            result_path = os.path.join(user_results_dir, result_filename)

            # Agregar la tarea en segundo plano para procesar cada hoja
            background_tasks.add_task(procesar_archivo, sheet_json_path, result_path, db, current_user, table_name)
        
        # Redirigir a la página de resultados
        return templates.TemplateResponse(
            "migraciones_nueva.html",
            {
                "request": request,
                "user": current_user,
                "message": "Archivo recibido. El procesamiento se realizará en segundo plano.",
                "result_url": f"/migraciones/control_migraciones"
            }
        )

    except Exception as e:
        logging.error(f"Error en el proceso de migración: {str(e)}")
        return templates.TemplateResponse(
            "migraciones_nueva.html",
            {
                "request": request,
                "user": current_user,
                "error": f"Error en el proceso: {str(e)}"
            }
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