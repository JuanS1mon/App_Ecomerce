import datetime
import pandas as pd
from fastapi import APIRouter, Request, status, Depends, HTTPException,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from Services.security.security import get_current_user
from db.database import get_db
from db.schemas.Maestro.Usuarios import UserDB
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.crud.tablas import get_tables, get_columns, get_table_data
from sqlalchemy import inspect, text
import numpy as np
from typing import Optional
from collections import Counter
from Services.Analisis.analisis import convert_types, limpiar_datos, guardar_resultados_sql


# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="static/html")

router = APIRouter(
    prefix="/analisis",
    tags=["Analisis"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

class ColumnasRequest(BaseModel):
    table_name: str

class AnalisisRequest(BaseModel):
    table_name: str
    column_name: str
    date_field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    additional_field: Optional[str] = None

class AnalisisDetalleRequest(BaseModel):
    table_name: str
    column_name: str
    date_field: str
    start_date: str
    end_date: str

@router.post("/columnas")
async def obtener_columnas(request: ColumnasRequest, db: Session = Depends(get_db)):
    table_name = request.table_name

    # Obtener las columnas de la tabla seleccionada
    inspector = inspect(db.bind)
    columns_info = inspector.get_columns(table_name)

    # Formatear la información de las columnas
    columns = [{"name": col["name"], "type": str(col["type"])} for col in columns_info]

    return {"columns": columns}



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

@router.post("/analizar_kpis")
async def analizar_kpis(request: AnalisisRequest, 
                        db: Session = Depends(get_db),
                        current_user: UserDB = Depends(get_current_user)):

    # Si no se proporciona la tabla, no hacemos nada
    if not request.table_name:
        return {"message": "No se proporcionó la tabla, no se ejecuta la consulta"}

    query_string = f"SELECT * FROM {request.table_name}"
    filters = []

    # Filtro por rango de fechas
    if request.date_field and request.start_date and request.end_date:
        filters.append(f"{request.date_field} BETWEEN '{request.start_date}' AND '{request.end_date}'")

    # Filtro adicional (ejemplo)
    if request.additional_field:
        filters.append(f"{request.additional_field} = 'valorX'")

    if filters:
        query_string += " WHERE " + " AND ".join(filters)

    df = pd.read_sql(text(query_string), db.bind)
    df = limpiar_datos(df)

    # Lógica para contar KPIs
    total_registros = len(df)
    categorias = df[request.column_name].nunique() if request.column_name in df.columns else 0
    last_date = df[request.date_field].max() if request.date_field in df.columns else None
    first_date = df[request.date_field].min() if request.date_field in df.columns else None
    max_value = df[request.column_name].max() if request.column_name in df.columns else None
    min_value = df[request.column_name].min() if request.column_name in df.columns else None

    # Lógica para contar clusters
    if request.column_name in df.columns:
        cluster_counts = Counter(df[request.column_name].dropna())
        clusters = dict(cluster_counts)
    else:
        clusters = {}

    resultados_kpis = {
        "total_registros": total_registros,
        "categorias": categorias,
        "last_date": convert_types(last_date),
        "first_date": convert_types(first_date),
        "max_value": convert_types(max_value),
        "min_value": convert_types(min_value),
        "clusters": clusters
    }
    guardar_resultados_sql(db, current_user.usuario, resultados_kpis)
    return resultados_kpis


@router.post("/analizar_detalle", response_class=JSONResponse)
async def analizar_detalle(analisis_request: AnalisisRequest, 
                           db: Session = Depends(get_db),
                           current_user: UserDB = Depends(get_current_user)):
    try:
        # Obtener los datos de la tabla con o sin filtros de fecha
        data = get_table_data(analisis_request.table_name, db, analisis_request.date_field, analisis_request.start_date, analisis_request.end_date)
        df = pd.DataFrame(data)
        
        # Manejar valores no compatibles con JSON
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

        # Convertir valores de fecha/hora a cadenas
        def convert_to_serializable(val):
            if isinstance(val, (pd.Timestamp, datetime.datetime, datetime.date)):
                return val.isoformat()
            elif isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                return None
            return val

        df = df.applymap(convert_to_serializable)

        # Convertir DataFrame a lista de diccionarios
        table_data = df.to_dict(orient="records") if not df.empty else []

        return JSONResponse(content={"records": table_data})
    except Exception as e:
        # Manejar cualquier excepción y devolver un error 500 con el mensaje de error
        return JSONResponse(status_code=500, content={"error": str(e)})




@router.post("/analizar_clasificacion")
async def analizar_clasificacion(request: AnalisisRequest, 
                                 db: Session = Depends(get_db),
                                 current_user: UserDB = Depends(get_current_user)):
    # Lógica de clasificación
    # ...
    return {"message": "Clasificación lista"}

@router.post("/analizar_regresion")
async def analizar_regresion(request: AnalisisRequest, 
                             db: Session = Depends(get_db),
                             current_user: UserDB = Depends(get_current_user)):
    # Lógica de regresión
    # ...
    return {"message": "Regresión lista"}