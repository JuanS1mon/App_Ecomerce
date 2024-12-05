# migraciones.py

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
    return templates.TemplateResponse("migracion.html", {"request": request, "user": current_user})

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
                "migracion.html",
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
                "migracion.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "El archivo está vacío."
                }
            )

        # Crear directorio del usuario si no existe
        user_results_dir = os.path.join(RESULTS_DIR, current_user.usuario)
        os.makedirs(user_results_dir, exist_ok=True)

        # Ruta donde se guardará el archivo JSON
        json_filename = "datos.json"
        json_path = os.path.join(user_results_dir, json_filename)

        # Ruta donde se guardará el resultado
        result_filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result_path = os.path.join(user_results_dir, result_filename)

        # Obtener la fecha y hora actual
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Nombre de la migración (obtenido del request)
        form = await request.form()
        nombre_migracion = form.get('migration_name', 'default_name')

        # Nombre de la tabla
        table_name = f"migracion_{nombre_migracion}_{timestamp}"

        # Agregar la tarea en segundo plano
        background_tasks.add_task(procesar_archivo, contents, json_path, result_path, db, current_user, table_name)

        # Redirigir a la página de resultados
        return templates.TemplateResponse(
            "migracion.html",
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
            "migracion.html",
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

        result_files = [f for f in os.listdir(user_results_dir) if f.startswith("result_") and f.endswith(".json")]
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
            "admin_migraciones.html",
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
    query = db.query(table).limit(5).all()
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

        # Insertar los datos en la tabla de destino
        db.execute(target_table.insert(), target_data)
        db.commit()

        return {"message": "Migración completada exitosamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al migrar datos: {str(e)}")