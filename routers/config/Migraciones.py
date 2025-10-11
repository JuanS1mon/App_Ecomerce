# migraciones.py

# Imports de bibliotecas estándar
import asyncio
import concurrent.futures
import json
import logging
import multiprocessing
import os
from datetime import datetime, timedelta
from io import BytesIO

# Imports de terceros
import pandas as pd
import psutil  # Para monitorear memoria
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
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
# from Services.Analisis.analisis import clean_data
# from Services.migracion.migracion import procesar_archivo

# Funciones stub temporales
def clean_data(data):
    """Función temporal stub para clean_data"""
    return data

def procesar_archivo(*args, **kwargs):
    """Función temporal stub para procesar_archivo"""
    pass
from security.auth_middleware import require_role_api
from db.crud.tablas import get_tables
from db.database import get_db
from db.models.config.activityLog import ActivityLog
from db.schemas.config.Usuarios import UserDB

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

# Configuración para procesamiento paralelo
MAX_WORKERS = min(multiprocessing.cpu_count(), 8)  # Máximo 8 procesos
CHUNK_SIZE = 100_000  # 100K filas por chunk
MEMORY_THRESHOLD = 80  # Porcentaje de memoria máximo antes de pausar


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
        # Métricas de subida (upload)
        self.stage = "idle"  # idle | uploading | processing | completed | error
        self.total_size_bytes = 0
        self.uploaded_bytes = 0
        self.upload_percentage = 0
        self.upload_speed_bps = 0  # bytes por segundo
        self.upload_eta_seconds = 0
        self.started_at = datetime.now().isoformat()

    def update(self, sheet_name: str, status: str, error: str = None):
        self.current_sheet = sheet_name
        self.status = status
        if error:
            self.errors.append({"sheet": sheet_name, "error": error})
        if status == "completado":
            self.processed_sheets += 1
            self.progress_percentage = (self.processed_sheets / self.total_sheets) * 100

    def update_upload(self, bytes_read: int, total_bytes: int, start_time: datetime):
        """Actualiza métricas de subida para feedback inmediato."""
        self.stage = "uploading"
        self.status = "subiendo archivo"
        # Configurar total si está disponible
        if total_bytes and total_bytes > 0:
            self.total_size_bytes = total_bytes
        self.uploaded_bytes += bytes_read
        # Calcular porcentaje (si se conoce total)
        if self.total_size_bytes and self.total_size_bytes > 0:
            self.upload_percentage = min(100.0, (self.uploaded_bytes / self.total_size_bytes) * 100.0)
        else:
            # Si no hay total conocido, aproximar usando progreso incremental
            self.upload_percentage = 0.0
        # Velocidad y ETA
        elapsed = (datetime.now() - start_time).total_seconds() or 0.000001
        self.upload_speed_bps = self.uploaded_bytes / elapsed
        if self.total_size_bytes and self.upload_speed_bps > 0:
            remaining = max(0, self.total_size_bytes - self.uploaded_bytes)
            self.upload_eta_seconds = remaining / self.upload_speed_bps
        else:
            self.upload_eta_seconds = 0

    def to_dict(self):
        """Convierte el objeto a un diccionario para serialización JSON"""
        return {
            "total_sheets": self.total_sheets,
            "processed_sheets": self.processed_sheets,
            "current_sheet": self.current_sheet,
            "status": self.status,
            "errors": self.errors,
            "progress_percentage": self.progress_percentage,
            "retry_count": self.retry_count,
            # Nuevos campos de estado/tiempo real
            "stage": getattr(self, "stage", "idle"),
            "total_size_bytes": getattr(self, "total_size_bytes", 0),
            "uploaded_bytes": getattr(self, "uploaded_bytes", 0),
            "upload_percentage": getattr(self, "upload_percentage", 0),
            "upload_speed_bps": getattr(self, "upload_speed_bps", 0),
            "upload_eta_seconds": getattr(self, "upload_eta_seconds", 0),
            "started_at": getattr(self, "started_at", None)
        }

class ParallelMigracionProgress(MigracionProgress):
    def __init__(self):
        super().__init__()
        self.total_chunks = 0
        self.processed_chunks = 0
        self.parallel_workers = 0
        self.memory_usage = 0
        self.processing_speed = 0  # filas por segundo
        self.estimated_time_remaining = 0

    def update_parallel(self, chunks_processed: int, memory_usage: float, speed: float):
        self.processed_chunks = chunks_processed
        self.memory_usage = memory_usage
        self.processing_speed = speed
        if speed > 0:
            remaining_chunks = self.total_chunks - self.processed_chunks
            self.estimated_time_remaining = remaining_chunks * CHUNK_SIZE / speed
        self.progress_percentage = (self.processed_chunks / self.total_chunks) * 100 if self.total_chunks > 0 else 0
        self.stage = "processing"

    def to_dict(self):
        """Convierte el objeto a un diccionario para serialización JSON"""
        base_dict = super().to_dict()
        base_dict.update({
            "total_chunks": self.total_chunks,
            "processed_chunks": self.processed_chunks,
            "parallel_workers": self.parallel_workers,
            "memory_usage": self.memory_usage,
            "processing_speed": self.processing_speed,
            "estimated_time_remaining": self.estimated_time_remaining
        })
        return base_dict

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

def process_chunk_worker(chunk_data, chunk_index, table_name, db_config):
    """Worker function para procesar un chunk en paralelo"""
    try:
        import pandas as pd
        from sqlalchemy import create_engine
        import json
        
        # Crear conexión independiente para este worker
        engine = create_engine(db_config['connection_string'])
        
        # Convertir chunk a DataFrame si no lo es ya
        if isinstance(chunk_data, list):
            df = pd.DataFrame(chunk_data)
        else:
            df = chunk_data
            
        # Limpiar datos
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        
        # Convertir tipos de datos problemáticos
        for col in df.columns:
            if df[col].dtype == 'object':
                # Intentar convertir fechas
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                except:
                    pass
        
        # Insertar en base de datos por chunks más pequeños
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            batch.to_sql(
                name=table_name,
                con=engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            total_inserted += len(batch)
        
        engine.dispose()
        
        return {
            'chunk_index': chunk_index,
            'rows_processed': total_inserted,
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'chunk_index': chunk_index,
            'rows_processed': 0,
            'status': 'error',
            'error': str(e)
        }

async def read_excel_in_chunks(file_path: str, chunk_size: int):
    """Lee archivo Excel por chunks"""
    chunks = []
    
    try:
        # Determinar motor según extensión
        engine = 'openpyxl' if file_path.endswith('.xlsx') else 'xlrd'
        
        with pd.ExcelFile(file_path, engine=engine) as xls:
            for sheet_name in xls.sheet_names:
                logging.info(f"Leyendo hoja: {sheet_name}")
                
                # Leer hoja completa primero (para archivos muy grandes, considerar usar chunksize)
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
                
                # Dividir en chunks
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i+chunk_size].copy()
                    if not chunk.empty:
                        chunks.append(chunk)
                
                del df  # Liberar memoria
                
    except Exception as e:
        logging.error(f"Error leyendo Excel: {str(e)}")
        raise
    
    return chunks

async def read_csv_in_chunks(file_path: str, chunk_size: int):
    """Lee archivo CSV por chunks"""
    chunks = []
    
    try:
        # Usar chunksize de pandas para archivos muy grandes
        chunk_reader = pd.read_csv(
            file_path,
            chunksize=chunk_size,
            encoding='utf-8-sig',
            low_memory=False
        )
        
        for chunk in chunk_reader:
            if not chunk.empty:
                chunks.append(chunk)
                
    except Exception as e:
        logging.error(f"Error leyendo CSV: {str(e)}")
        raise
    
    return chunks

async def process_large_file_parallel(
    file_path: str,
    nombre_migracion: str,
    timestamp: str,
    user_results_dir: str,
    db: Session,
    current_user: UserDB,
    progress: ParallelMigracionProgress,
    file_type: str = 'excel'
):
    """Procesa archivos grandes en paralelo"""
    try:
        progress.status = "analizando archivo"
        progress.stage = "processing"
        logging.info(f"Iniciando procesamiento paralelo de {file_path}")
        
        # Obtener configuración de base de datos
        db_config = {
            'connection_string': str(db.get_bind().url)
        }
        
        # Leer archivo por chunks según el tipo
        if file_type == 'excel':
            chunks = await read_excel_in_chunks(file_path, CHUNK_SIZE)
        else:  # CSV
            chunks = await read_csv_in_chunks(file_path, CHUNK_SIZE)

        progress.total_chunks = len(chunks)
        progress.parallel_workers = MAX_WORKERS
        progress.status = "procesando en paralelo"
        
        # Crear tabla base
        table_name = f"migracion_{nombre_migracion}_{timestamp}".replace(" ", "_").lower()
        
        # Usar ThreadPoolExecutor para I/O intensivo o ProcessPoolExecutor para CPU intensivo
        executor_class = ProcessPoolExecutor if len(chunks) > 50 else ThreadPoolExecutor
        
        async def process_chunks_batch(chunk_batch, batch_start_index):
            """Procesa un lote de chunks"""
            loop = asyncio.get_event_loop()
            
            with executor_class(max_workers=MAX_WORKERS) as executor:
                # Crear tareas para cada chunk en el lote
                tasks = []
                for i, chunk in enumerate(chunk_batch):
                    chunk_index = batch_start_index + i
                    task = loop.run_in_executor(
                        executor,
                        process_chunk_worker,
                        chunk,
                        chunk_index,
                        table_name,
                        db_config
                    )
                    tasks.append(task)
                
                # Esperar a que todos los chunks del lote se completen
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return results
        
        # Procesar en lotes para controlar memoria
        batch_size = MAX_WORKERS * 2  # Procesar 2 lotes por worker
        total_processed = 0
        total_errors = 0
        start_time = datetime.now()
        
        for batch_start in range(0, len(chunks), batch_size):
            # Verificar uso de memoria antes de cada lote
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > MEMORY_THRESHOLD:
                logging.warning(f"Memoria alta ({memory_percent}%), pausando 10 segundos...")
                await asyncio.sleep(10)
                continue
            
            batch_end = min(batch_start + batch_size, len(chunks))
            chunk_batch = chunks[batch_start:batch_end]
            
            # Procesar lote
            results = await process_chunks_batch(chunk_batch, batch_start)
            
            # Procesar resultados
            for result in results:
                if isinstance(result, Exception):
                    total_errors += 1
                    progress.errors.append({"chunk": "unknown", "error": str(result)})
                elif result['status'] == 'success':
                    total_processed += result['rows_processed']
                else:
                    total_errors += 1
                    progress.errors.append({
                        "chunk": result['chunk_index'], 
                        "error": result.get('error', 'Unknown error')
                    })
            
            # Actualizar progreso
            elapsed_time = (datetime.now() - start_time).total_seconds()
            speed = total_processed / elapsed_time if elapsed_time > 0 else 0
            memory_usage = psutil.virtual_memory().percent
            
            progress.update_parallel(
                chunks_processed=batch_end,
                memory_usage=memory_usage,
                speed=speed
            )
            
            logging.info(f"Lote {batch_start//batch_size + 1} completado. "
                        f"Procesadas {total_processed} filas, {total_errors} errores. "
                        f"Velocidad: {speed:.0f} filas/seg")
        
        # Actualizar estado final
        if total_errors > 0:
            progress.status = f"completado con {total_errors} errores"
        else:
            progress.status = "completado exitosamente"
        progress.stage = "completed"
        
        # Crear archivo de resultado
        result_data = {
            "status": progress.status,
            "total_rows_processed": total_processed,
            "total_errors": total_errors,
            "processing_time_seconds": elapsed_time,
            "average_speed": speed,
            "table_name": table_name,
            "timestamp": timestamp
        }
        
        result_path = os.path.join(user_results_dir, f"result_parallel_{timestamp}.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # Limpiar chunks de memoria
        del chunks
        import gc
        gc.collect()
        
        # Eliminar archivo temporal
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logging.info(f"Procesamiento paralelo completado: {total_processed} filas, {elapsed_time:.1f}s")
        
    except Exception as e:
        error_msg = f"Error en procesamiento paralelo: {str(e)}"
        logging.error(error_msg)
        progress.status = "error"
        progress.errors.append({"chunk": "general", "error": error_msg})

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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """Sube y procesa archivos de migración con procesamiento paralelo para archivos grandes"""
    try:
        # Obtener información del usuario
        user_id = current_user.codigo
        user_name = current_user.usuario
        
        if not user_id or not user_name:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        # Validar tamaño del archivo (aumentamos el límite para archivos grandes)
        max_size = 50 * 1024 * 1024 * 1024  # 50GB máximo
        if file.size and file.size > max_size:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 50GB)")
        
        # Validar extensión del archivo
        if not file.filename or not any(file.filename.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        # Determinar tamaño si el cliente lo envía; UploadFile.size puede ser None
        total_size_bytes = 0
        try:
            total_size_bytes = int(file.size or 0)
        except Exception:
            total_size_bytes = 0
        # Usar progreso paralelo para archivos grandes
        file_size_gb = (total_size_bytes or 0) / (1024**3)
        use_parallel = file_size_gb > 1.0  # Usar paralelo para archivos > 1GB
        
        if use_parallel:
            progress = ParallelMigracionProgress()
            logging.info(f"Archivo grande detectado ({file_size_gb:.1f}GB), usando procesamiento paralelo")
        else:
            progress = MigracionProgress()
            logging.info(f"Archivo pequeño ({file_size_gb:.1f}GB), usando procesamiento secuencial")

        progress_storage[user_name] = progress
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Configuración inicial
        user_results_dir = os.path.join(RESULTS_DIR, user_name)
        os.makedirs(user_results_dir, exist_ok=True)
        form = await request.form()
        nombre_migracion = form.get('migration_name', 'default_name')
        
        # Sanitizar nombre de migración
        nombre_migracion = "".join(c for c in nombre_migracion if c.isalnum() or c in ['_', '-']).lower()
        
        # Guardar archivo temporalmente
        temp_file_path = os.path.join(user_results_dir, f"temp_{timestamp}_{file.filename}")

        # Usar chunks más grandes para archivos grandes
        UPLOAD_CHUNK_SIZE = 10 * 1024 * 1024 if use_parallel else 1024 * 1024  # 10MB o 1MB
        
        try:
            progress.stage = "uploading"
            progress.total_size_bytes = total_size_bytes
            upload_start = datetime.now()
            with open(temp_file_path, 'wb') as f:
                while True:
                    chunk = await file.read(UPLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    # Actualizar progreso de subida
                    progress.update_upload(bytes_read=len(chunk), total_bytes=total_size_bytes, start_time=upload_start)
            # Marcar fin de subida
            progress.stage = "processing"
            progress.status = "archivo cargado, iniciando procesamiento"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")
        
        # Determinar tipo de archivo y procesar
        file_type = 'excel' if file.filename.lower().endswith(('.xlsx', '.xls')) else 'csv'
        
        if use_parallel:
            # Procesamiento paralelo para archivos grandes
            background_tasks.add_task(
                process_large_file_parallel,
                temp_file_path,
                nombre_migracion,
                timestamp,
                user_results_dir,
                db,
                current_user,
                progress,
                file_type
            )
        else:
            # Procesamiento secuencial para archivos pequeños
            if file_type == 'excel':
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
            else:  # CSV
                # El stream ya fue consumido para guardar en temp_file_path; leer desde disco
                with open(temp_file_path, 'rb') as temp_f:
                    contents = temp_f.read()
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

        return JSONResponse(content={
            "message": f"Archivo recibido ({file_size_gb:.1f}GB). Procesamiento {'paralelo' if use_parallel else 'secuencial'} iniciado.",
            "processing_type": "parallel" if use_parallel else "sequential",
            "estimated_chunks": int(file_size_gb * 1000) if use_parallel else 1,
            "max_workers": MAX_WORKERS if use_parallel else 1,
            "chunk_size": CHUNK_SIZE if use_parallel else "N/A",
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """Página índice de migraciones - redirige a admin_migraciones"""
    return RedirectResponse(url="/migraciones/admin_migraciones", status_code=302)

# Agregar endpoint para estadísticas de migraciones
@router.get("/api/stats")
async def get_migration_stats(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
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

# Endpoint adicional para monitorear recursos del sistema
@router.get("/api/system_resources")
async def get_system_resources(
    current_user: UserDB = Depends(require_role_api(["admin", "usuario"]))
):
    """Obtiene información sobre recursos del sistema"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage_percent": psutil.disk_usage('.').percent,
            "active_connections": len(psutil.net_connections()),
            "max_workers": MAX_WORKERS,
            "chunk_size": CHUNK_SIZE,
            "memory_threshold": MEMORY_THRESHOLD
        }
    except Exception as e:
        logging.error(f"Error obteniendo recursos del sistema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))