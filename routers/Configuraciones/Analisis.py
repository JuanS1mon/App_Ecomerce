import datetime
import pandas as pd
import numpy as np
from fastapi import APIRouter, Request, logger, status, Depends, HTTPException,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from Services.security.security import get_current_user
from db.database import get_db
from db.schemas.Maestro.Usuarios import UserDB
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.crud.tablas import get_tables, get_columns, get_table_data
from sqlalchemy import inspect, text
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
    additional_field: Optional[str] = None  # Campos adicionales separados por comas

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
    try:
        if not request.table_name:
            return {"message": "No se proporcionó la tabla, no se ejecuta la consulta"}

        # Función auxiliar para escapar nombres de columnas
        def escape_column(column_name):
            return f"[{column_name}]"

        query_string = f"SELECT * FROM {escape_column(request.table_name)}"
        filters = []

        # Filtro por rango de fechas con nombre de columna escapado
        if request.date_field and request.start_date and request.end_date:
            filters.append(
                f"{escape_column(request.date_field)} BETWEEN '{request.start_date}' AND '{request.end_date}'"
            )

        # Procesar campos adicionales si existen
        campos_adicionales = []
        if request.additional_field:
            campos_adicionales = [campo.strip() for campo in request.additional_field.split(',') if campo.strip()]
            for campo in campos_adicionales:
                filters.append(f"{escape_column(campo)} IS NOT NULL")

        if filters:
            query_string += " WHERE " + " AND ".join(filters)

        df = pd.read_sql(text(query_string), db.bind)
        df = limpiar_datos(df)

        # Lógica para contar KPIs
        total_registros = len(df)
        
        # Análisis del campo principal para max/min (siempre del campo principal)
        try:
            serie_principal = pd.to_numeric(df[request.column_name], errors='coerce')
            max_value = float(serie_principal.max()) if not pd.isna(serie_principal.max()) else None
            min_value = float(serie_principal.min()) if not pd.isna(serie_principal.min()) else None
        except:
            max_value = None
            min_value = None

        # Análisis de categorías (usando el campo principal)
        categorias_dict = df[request.column_name].value_counts().to_dict()
        categorias = len(categorias_dict)

        # Análisis de clusters temporales y numéricos
        clusters_dict = {}
        
        # Clusters temporales si hay campo de fecha
        if request.date_field and request.date_field in df.columns:
            df[request.date_field] = pd.to_datetime(df[request.date_field], errors='coerce')
            
            # Análisis por año
            clusters_dict['temporal'] = {
                'por_año': df[request.date_field].dt.year.value_counts().sort_index().to_dict(),
                
                # Análisis por mes del año actual
                'por_mes': df[df[request.date_field].dt.year == datetime.datetime.now().year][request.date_field]
                    .dt.month.value_counts().sort_index().to_dict(),
                
                # Análisis por día de la semana
                'por_dia_semana': df[request.date_field].dt.dayofweek.map({
                    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
                    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
                }).value_counts().to_dict(),
                
                # Análisis por trimestre
                'por_trimestre': df[request.date_field].dt.quarter.value_counts().sort_index().to_dict()
            }

            # Tendencia mensual (últimos 12 meses)
            fecha_max = df[request.date_field].max()
            if fecha_max is not None:
                ultimos_12_meses = df[
                    df[request.date_field] >= (fecha_max - pd.DateOffset(months=12))
                ]
                tendencia_mensual = ultimos_12_meses.groupby(
                    ultimos_12_meses[request.date_field].dt.to_period('M')
                ).size()
                clusters_dict['temporal']['tendencia_12_meses'] = {
                    str(k): int(v) for k, v in tendencia_mensual.items()
                }

        # Clusters por rangos numéricos para campos adicionales
        if campos_adicionales:
            clusters_dict['numericos'] = {}
            for campo in campos_adicionales:
                if campo in df.columns:
                    try:
                        serie = pd.to_numeric(df[campo], errors='coerce')
                        if not serie.isna().all():
                            # Crear clusters por rangos usando quantiles
                            q_labels = ['Muy Bajo', 'Bajo', 'Medio', 'Alto', 'Muy Alto']
                            serie_clusters = pd.qcut(
                                serie, 
                                q=5, 
                                labels=q_labels, 
                                duplicates='drop'
                            )
                            clusters_dict['numericos'][campo] = serie_clusters.value_counts().to_dict()
                    except:
                        continue

        # Fechas
        if request.date_field in df.columns:
            last_date = df[request.date_field].max()
            first_date = df[request.date_field].min()
        else:
            last_date = None
            first_date = None

        # Análisis detallado por campo
        analisis_por_campo = {
            "principal": {
                "campo": request.column_name,
                "categorias": categorias,
                "distribucion": categorias_dict
            }
        }

        # Agregar análisis de campos adicionales
        for i, campo in enumerate(campos_adicionales, 1):
            if campo in df.columns:
                analisis_por_campo[f"adicional_{i}"] = {
                    "campo": campo,
                    "categorias": df[campo].nunique(),
                    "distribucion": df[campo].value_counts().to_dict()
                }

        resultados_kpis = {
            "total_registros": total_registros,
            "categorias": categorias,
            "categorias_detalle": categorias_dict,
            "max_value": max_value,
            "min_value": min_value,
            "clusters": clusters_dict,
            "last_date": convert_types(last_date),
            "first_date": convert_types(first_date),
            "analisis_campos": analisis_por_campo
        }

        # Guardar resultados
        guardar_resultados_sql(db, current_user.usuario, {
            "total_registros": total_registros,
            "categorias": categorias,
            "last_date": convert_types(last_date) or None,
            "first_date": convert_types(first_date) or None,
            "max_value": max_value,
            "min_value": min_value,
            "clusters": str(clusters_dict)
        })

        return resultados_kpis

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al analizar los datos: {str(e)}"}
        )


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

        df = df.apply(lambda col: col.apply(convert_to_serializable))

        # Convertir DataFrame a lista de diccionarios
        table_data = df.to_dict(orient="records") if not df.empty else []

        return JSONResponse(content={"records": table_data})
    except Exception as e:
        # Manejar cualquier excepción y devolver un error 500 con el mensaje de error
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/analizar_grafico")
async def analizar_grafico(request: AnalisisRequest,
                          db: Session = Depends(get_db),
                          current_user: UserDB = Depends(get_current_user)):
    try:
        if not request.table_name or not request.date_field:
            return {"message": "Se requiere tabla y campo de fecha"}

        # Función auxiliar para escapar nombres de columnas
        def escape_column(column_name):
            return f"[{column_name}]"

        # Construir query optimizada con nombres escapados
        campos_select = [escape_column(request.date_field)]
        if request.column_name:
            campos_select.append(escape_column(request.column_name))
            
        # Procesar campos adicionales
        campos_adicionales = []
        if request.additional_field:
            campos_adicionales = [campo.strip() for campo in request.additional_field.split(',') if campo.strip()]
            campos_select.extend(escape_column(campo) for campo in campos_adicionales)

        # Construir query con nombres escapados
        query_string = f"SELECT {', '.join(campos_select)} FROM {escape_column(request.table_name)}"
        
        # Filtros de fecha con nombre escapado
        if request.start_date and request.end_date:
            query_string += f" WHERE {escape_column(request.date_field)} BETWEEN '{request.start_date}' AND '{request.end_date}'"

        print(f"Query ejecutada: {query_string}")  # Para debugging

        # Cargar y preparar datos
        df = pd.read_sql(text(query_string), db.bind)
        df = limpiar_datos(df)
        
        # Convertir fecha de manera segura
        df[request.date_field] = pd.to_datetime(df[request.date_field], errors='coerce')
        
        graficos_data = {
            "series_temporales": {},
            "metadata": {
                "fecha_inicio": request.start_date,
                "fecha_fin": request.end_date,
                "total_registros": len(df)
            }
        }

        ## Análisis temporal para cada campo
        for campo in [request.column_name] + campos_adicionales:
            if campo and campo in df.columns:
                try:
                    # Determinar si el campo es numérico de manera más robusta
                    es_numerico = pd.api.types.is_numeric_dtype(df[campo]) or (
                        pd.to_numeric(df[campo], errors='coerce').notna().any() and 
                        not df[campo].dtype == 'object'
                    )
                    
                    if not es_numerico:
                        # Para campos categóricos
                        df_agrupado = df.groupby([
                            df[request.date_field].dt.strftime('%Y-%m-%d'),
                            campo
                        ]).size().unstack(fill_value=0)
                        
                        # Asegurar que tenemos todas las categorías
                        categorias = df[campo].unique()
                        for cat in categorias:
                            if cat not in df_agrupado.columns:
                                df_agrupado[cat] = 0
                        
                        # Preparar datos para el gráfico
                        graficos_data["series_temporales"][campo] = {
                            "fechas": df_agrupado.index.tolist(),
                            "valores": {
                                str(cat): df_agrupado[cat].tolist() 
                                for cat in df_agrupado.columns
                            },
                            "tipo": "categorico",
                            "categorias": [str(cat) for cat in df_agrupado.columns]
                        }
                    else:
                        # Para campos numéricos, mantener el código existente
                        datos_numericos = df.groupby(
                            df[request.date_field].dt.strftime('%Y-%m-%d')
                        )[campo].agg(['mean', 'sum', 'count']).reset_index()
                        
                        graficos_data["series_temporales"][campo] = {
                            "fechas": datos_numericos[request.date_field].tolist(),
                            "valores": {
                                "promedio": datos_numericos['mean'].tolist(),
                                "suma": datos_numericos['sum'].tolist(),
                                "conteo": datos_numericos['count'].tolist()
                            },
                            "tipo": "numerico"
                        }

                except Exception as e:
                    print(f"Error procesando campo {campo}: {str(e)}")
                    continue

        return {
            "status": "success",
            "data": graficos_data
        }

    except Exception as e:
        print(f"Error en análisis gráfico: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error en análisis gráfico: {str(e)}"}
        )
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