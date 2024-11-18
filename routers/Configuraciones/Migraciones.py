# Migraciones.py

import os
import logging
from fastapi import APIRouter, Request, status, Depends, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from Services.security.security import get_current_user
import pandas as pd
from io import BytesIO
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, BigInteger
from db.database import get_db
from db.models.activityLog import ActivityLog
from db.models.usuarios import usuarios


# Configuración de logging
logging.basicConfig(
    filename='logs/migraciones.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
JSON_DIR = os.path.join(BASE_DIR, "json_output")

# Crear directorios si no existen
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="static/html")

router = APIRouter(
    prefix="/migraciones",
    tags=["Migraciones"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

def eanCheck(ean):
    """Validación mejorada de códigos EAN"""
    try:
        if not ean or not str(ean).strip().isdigit():
            return False
        ean = str(ean).strip()
        if len(ean) not in [8, 12, 13]:
            return False
        checksum = 0
        for i, digit in enumerate(reversed(ean[:-1])):
            checksum += int(digit) * (3 if i % 2 == 0 else 1)
        check_digit = (10 - (checksum % 10)) % 10
        return check_digit == int(ean[-1])
    except Exception as e:
        logging.error(f"Error en validación EAN: {str(e)}")
        return False

def modificar_ean(valor):
    """Función mejorada para modificar códigos EAN"""
    try:
        if pd.isna(valor):
            return None
        valor_str = str(int(valor)).strip()
        if len(valor_str) == 13:
            if eanCheck(valor_str):
                return int(valor_str[:-1])
            logging.warning(f"EAN-13 inválido: {valor_str}")
            return None
        elif len(valor_str) == 12:
            return int(valor_str[:-1])
        elif len(valor_str) == 8:
            return int(valor_str[:-1])
        elif len(valor_str) in [11, 7]:
            return int(valor_str)
        else:
            logging.warning(f"Longitud EAN inválida: {valor_str}")
            return None
    except Exception as e:
        logging.error(f"Error procesando EAN: {str(e)}")
        return None

def limpiar_datos(df):
    """Limpia y valida los datos del DataFrame"""
    for column in df.select_dtypes(include=['float64']).columns:
        df[column] = df[column].apply(lambda x: 0 if pd.isna(x) else x)
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: '' if pd.isna(x) else str(x).strip())
    for column in df.select_dtypes(include=['int64']).columns:
        df[column] = df[column].apply(lambda x: 0 if pd.isna(x) else x)
    return df

def convertir_a_int(valor):
    """Convierte valores numéricos a enteros si es posible"""
    try:
        return int(valor)
    except (ValueError, TypeError):
        return valor

def convertir_a_float(valor):
    """Convierte valores numéricos a flotantes si es posible"""
    try:
        return float(valor)
    except (ValueError, TypeError):
        return valor

@router.get("/page")
async def migraciones_page(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    return templates.TemplateResponse("migracion.html", {"request": request, "username": current_user})

@router.post("/upload")
async def upload_migracion_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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

        # Procesar Excel
        try:
            df = pd.read_excel(BytesIO(contents), engine='openpyxl')
        except Exception as e:
            logging.warning(f"Fallo al leer con openpyxl: {str(e)}. Intentando con xlrd.")
            try:
                df = pd.read_excel(BytesIO(contents), engine='xlrd')
            except Exception as e:
                logging.error(f"Fallo al leer con xlrd: {str(e)}")
                return templates.TemplateResponse(
                    "migracion.html",
                    {
                        "request": request,
                        "user": current_user,
                        "error": "No se pudo leer el archivo Excel. Asegúrese de que el archivo esté en un formato válido."
                    }
                )

        if df.empty:
            return templates.TemplateResponse(
                "migracion.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "El archivo Excel no contiene datos."
                }
            )

        # Contador de registros originales
        total_registros = len(df)

        # Limpiar y validar datos
        df = limpiar_datos(df)

        # Inicializar contadores
        registros_no_guardados = []
        registros_procesados = 0

        # Procesar EAN si la columna existe
        if 'EAN' in df.columns:
            df['EAN'] = pd.to_numeric(df['EAN'], errors='coerce')
            
            # Registros no numéricos
            registros_no_numericos = df[df['EAN'].isna()]
            if not registros_no_numericos.empty:
                registros_no_guardados.extend(registros_no_numericos.to_dict(orient='records'))
                df = df.drop(registros_no_numericos.index)

            # Procesar EAN válidos
            df['EAN_MODIFICADO'] = df['EAN'].apply(modificar_ean)
            
            # Registros con EAN inválidos
            registros_ean_invalidos = df[df['EAN_MODIFICADO'].isna()]
            if not registros_ean_invalidos.empty:
                registros_no_guardados.extend(registros_ean_invalidos.to_dict(orient='records'))
                df = df.drop(registros_ean_invalidos.index)

            df['EAN'] = df['EAN_MODIFICADO']
            df = df.drop(columns=['EAN_MODIFICADO'])

        # Convertir valores numéricos a enteros o flotantes si es posible
        for record in df.to_dict(orient='records'):
            for key, value in record.items():
                if isinstance(value, float):
                    record[key] = convertir_a_float(value)
                else:
                    record[key] = convertir_a_int(value)

        # Crear tabla dinámica
        metadata = MetaData()
        columns = [Column('id', BigInteger, primary_key=True, autoincrement=True)]
        
        type_mapping = {
            'int64': BigInteger,
            'float64': Float,
            'object': String,
            'bool': Boolean,
            'datetime64[ns]': DateTime,
            'biginteger': BigInteger  # Ajustar para EAN
        }

        for column_name in df.columns:
            pandas_type = str(df[column_name].dtype)
            if column_name == 'EAN':
                column_type = BigInteger  # Ajustar para EAN
            elif column_name == 'Codigo_DUN' or column_name == 'Cantidad_DUN':
                column_type = BigInteger  # Ajustar para valores grandes
            else:
                column_type = type_mapping.get(pandas_type, String)
            columns.append(Column(column_name, column_type))

        # Nombre de tabla con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = f"migracion_{timestamp}"

        # Crear tabla
        dynamic_table = Table(table_name, metadata, *columns)
        metadata.create_all(db.get_bind(), tables=[dynamic_table])

        # Insertar datos
        records = df.to_dict(orient='records')
        registros_procesados = 0
        
        for record in records:
            try:
                with db.begin():
                    db.execute(dynamic_table.insert(), [record])
                registros_procesados += 1
            except Exception as e:
                logging.error(f"Error al insertar registro: {str(e)}")
                registros_no_guardados.append(record)

        # Guardar registros no válidos
        if registros_no_guardados:
            json_path = os.path.join(JSON_DIR, f"invalidos_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(registros_no_guardados, f, ensure_ascii=False, indent=4)
            
            logging.warning(f"Registros no guardados: {len(registros_no_guardados)}")

        # Calcular porcentaje de registros cargados
        porcentaje_cargados = (registros_procesados / total_registros) * 100

        # Log del resultado
        logging.info(f"Migración completada: {registros_procesados} registros procesados, "
                    f"{len(registros_no_guardados)} registros inválidos, "
                    f"{porcentaje_cargados:.2f}% de registros cargados")

        # Buscar el usuario por nombre de usuario
        usuario = db.query(usuarios).filter(usuarios.usuario == current_user['username']).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Registrar la actividad
        new_activity = ActivityLog(
            usuario_id=usuario.codigo,
            action=f"Realizó una migración de datos el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        db.add(new_activity)
        db.commit()

        return templates.TemplateResponse(
            "migracion.html",
            {
                "request": request,
                "user": current_user,
                "message": f"Proceso completado. {registros_procesados} registros guardados, "
                          f"{len(registros_no_guardados)} registros inválidos. "
                          f"{porcentaje_cargados:.2f}% de registros cargados.",
                "registros_invalidos": len(registros_no_guardados) > 0,
                "tabla_generada": table_name
            }
        )

    except pd.errors.EmptyDataError:
        logging.error("Archivo Excel vacío")
        return templates.TemplateResponse(
            "migracion.html",
            {
                "request": request,
                "user": current_user,
                "error": "El archivo Excel está vacío o no contiene datos legibles."
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