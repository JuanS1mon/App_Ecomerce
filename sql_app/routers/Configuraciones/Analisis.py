import logging
from sklearn.cluster import KMeans
import pandas as pd
from fastapi import APIRouter, Request, status, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from Services.security.security import get_current_user
from db.database import get_db
from db.schemas.Maestro.Usuarios import UserDB
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.crud.tablas import get_tables,get_columns
from sqlalchemy import text
import numpy as np

# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="static/html")

router = APIRouter(
    prefix="/analisis",
    tags=["Analisis"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)


class ColumnasRequest(BaseModel):
    table_name: str

@router.post("/columnas")
async def obtener_columnas(request: ColumnasRequest, db: Session = Depends(get_db)):
    table_name = request.table_name

    # Obtener las columnas de la tabla seleccionada
    query = text(f"SELECT TOP 1 * FROM {table_name}")
    df = pd.read_sql(query, db.bind)
    columns = df.columns.tolist()

    return {"columns": columns}

class AnalisisRequest(BaseModel):
    table_name: str

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # Ejemplo de datos para el gráfico
    chart_data = {
        "labels": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "values": [10, 20, 30]
    }
    return templates.TemplateResponse("analisis_admin.html", {"request": request, "user": current_user, "chart_data": chart_data})


@router.get("/nuevo", response_class=HTMLResponse)
async def nuevo_analisis_page(request: Request, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    _, tabla2 = get_tables(db)  # Obtener tabla2
    return templates.TemplateResponse("analisis_new.html", {"request": request, "user": current_user, "tabla2": tabla2})
class AnalisisRequest(BaseModel):
    table_name: str
    column_name: str

class AnalisisRequest(BaseModel):
    table_name: str
    column_name: str

@router.post("/analizar")
async def analizar_datos(request: AnalisisRequest, db: Session = Depends(get_db)):
    table_name = request.table_name
    column_name = request.column_name

    # Obtener los datos de la tabla seleccionada
    query = text(f"SELECT * FROM {table_name}")
    df = pd.read_sql(query, db.bind)

    # Convertir la columna 'fecha' a tipo datetime
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

    # Realizar análisis de datos
    total_registros = int(len(df))
    categorias = int(df['categoria'].nunique()) if 'categoria' in df.columns else 0
    last_date = df['fecha'].max().strftime('%Y-%m-%d') if 'fecha' in df.columns else None
    first_date = df['fecha'].min().strftime('%Y-%m-%d') if 'fecha' in df.columns else None

    # Manejar diferentes tipos de datos en la columna seleccionada
    if pd.api.types.is_numeric_dtype(df[column_name]):
        max_value = float(df[column_name].max()) if column_name in df.columns else None
        min_value = float(df[column_name].min()) if column_name in df.columns else None
    elif pd.api.types.is_datetime64_any_dtype(df[column_name]):
        max_value = df[column_name].max().strftime('%Y-%m-%d %H:%M:%S') if column_name in df.columns else None
        min_value = df[column_name].min().strftime('%Y-%m-%d %H:%M:%S') if column_name in df.columns else None
    else:
        max_value = str(df[column_name].max()) if column_name in df.columns else None
        min_value = str(df[column_name].min()) if column_name in df.columns else None

    # Preparar datos para el gráfico
    chart_data = {
        "labels": df['fecha'].unique().tolist() if 'fecha' in df.columns else [],
        "values": df.groupby('fecha').size().tolist() if 'fecha' in df.columns else []
    }

    # Aplicar KMeans para clustering
    clusters = []
    if column_name in df.columns:
        # Verificar si hay valores nulos en la columna seleccionada
        if df[column_name].isnull().any():
            logging.warning(f"La columna '{column_name}' contiene valores nulos. Estos valores serán eliminados.")
            df = df.dropna(subset=[column_name])

        # Verificar si la columna seleccionada contiene datos numéricos
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            logging.warning(f"La columna '{column_name}' contiene datos no numéricos. Intentando convertir a numérico.")
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
            df = df.dropna(subset=[column_name])

        logging.info(f"Datos para clustering después de limpieza: {df[[column_name]].head()}")

        if not df.empty:
            kmeans = KMeans(n_clusters=3)
            df['cluster'] = kmeans.fit_predict(df[[column_name]])
            clusters = df['cluster'].tolist()
            logging.info(f"Clusters generados: {clusters}")
        else:
            logging.warning(f"No hay datos suficientes en la columna '{column_name}' para realizar clustering.")
    else:
        logging.warning(f"La columna '{column_name}' no existe en el DataFrame.")

    return {
        "total_registros": total_registros,
        "categorias": categorias,
        "last_date": last_date,
        "first_date": first_date,
        "max_value": max_value,
        "min_value": min_value,
        "chart_data": chart_data,
        "table_data": df.to_dict(orient='records'),
        "clusters": clusters
    }