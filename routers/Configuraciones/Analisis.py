import logging
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import pandas as pd
from fastapi import APIRouter, Request, status, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from Services.security.security import get_current_user
from db.database import get_db
from db.schemas.Maestro.Usuarios import UserDB
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.crud.tablas import get_tables, get_columns
from sqlalchemy import inspect, text
import numpy as np
import json
import os

# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="static/html")

router = APIRouter(
    prefix="/analisis",
    tags=["Analisis"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

class ColumnasRequest(BaseModel):
    table_name: str
    

class ColumnasRequest(BaseModel):
    table_name: str

@router.post("/columnas")
async def obtener_columnas(request: ColumnasRequest, db: Session = Depends(get_db)):
    table_name = request.table_name

    # Obtener las columnas de la tabla seleccionada
    inspector = inspect(db.bind)
    columns_info = inspector.get_columns(table_name)

    # Formatear la información de las columnas
    columns = [{"name": col["name"], "type": str(col["type"])} for col in columns_info]

    return {"columns": columns}

class AnalisisRequest(BaseModel):
    table_name: str
    column_name: str

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

@router.post("/analizar")
async def analizar_datos(request: AnalisisRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    table_name = request.table_name
    column_name = request.column_name

    # Obtener los datos de la tabla seleccionada
    query = text(f"SELECT * FROM {table_name}")
    df = pd.read_sql(query, db.bind)

    # Limpiar los datos
    df = limpiar_datos(df)

    # Convertir la columna 'fecha' a tipo datetime si existe
    if 'fecha' in df.columns:
        df['fecha_str'] = df['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        df['fecha_str'] = None

    # Realizar análisis de datos
    total_registros = int(len(df))
    categorias = int(df['categoria'].nunique()) if 'categoria' in df.columns else 0
    last_date = df['fecha'].max().strftime('%Y-%m-%d %H:%M:%S') if 'fecha' in df.columns else None
    first_date = df['fecha'].min().strftime('%Y-%m-%d %H:%M:%S') if 'fecha' in df.columns else None

    # Manejar diferentes tipos de datos en la columna seleccionada
    if pd.api.types.is_numeric_dtype(df[column_name]):
        max_value = float(df[column_name].max())
        min_value = float(df[column_name].min())
        total_sum = float(df[column_name].sum())
        average = float(df[column_name].mean())
    elif pd.api.types.is_datetime64_any_dtype(df[column_name]):
        max_value = df[column_name].max().strftime('%Y-%m-%d %H:%M:%S')
        min_value = df[column_name].min().strftime('%Y-%m-%d %H:%M:%S')
        total_sum = None
        average = None
    else:
        max_value = str(df[column_name].max())
        min_value = str(df[column_name].min())
        total_sum = None
        average = None

    # Calcular el promedio por fecha si la columna 'fecha' existe
    if 'fecha' in df.columns and pd.api.types.is_numeric_dtype(df[column_name]):
        promedio_por_fecha = df.groupby('fecha')[column_name].mean().reset_index()
        promedio_por_fecha['fecha'] = promedio_por_fecha['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
        promedio_por_fecha = promedio_por_fecha.to_dict(orient='records')
    else:
        promedio_por_fecha = []

    # Preparar datos para el gráfico utilizando 'fecha_str'
    if 'fecha_str' in df.columns and df['fecha_str'].notnull().any():
        chart_data = {
            "labels": df['fecha_str'].unique().tolist(),
            "values": df.groupby('fecha_str').size().tolist()
        }
    else:
        chart_data = {
            "labels": [],
            "values": []
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

        if not df.empty:
            kmeans = KMeans(n_clusters=3)
            df['cluster'] = kmeans.fit_predict(df[[column_name]])
            clusters = df['cluster'].tolist()
        else:
            logging.warning(f"No hay datos suficientes en la columna '{column_name}' para realizar clustering.")

    # Convertir objetos Timestamp a cadenas de texto en 'table_data'
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Preparar los resultados
    resultados = {
        "user_id": current_user.usuario,
        "table_name": table_name,
        "column_name": column_name,
        "total_registros": total_registros,
        "categorias": categorias,
        "last_date": last_date,
        "first_date": first_date,
        "max_value": max_value,
        "min_value": min_value,
        "total_sum": total_sum,
        "average": average,
        "promedio_por_fecha": promedio_por_fecha,
        "chart_data": chart_data,
        "table_data": df_copy.to_dict(orient='records'),
        "clusters": clusters
    }

    # Guardar los resultados en un archivo JSON
    guardar_resultados_json(current_user.usuario, resultados)

    return resultados
    
def guardar_resultados_json(user_id, resultados):
    # Crear el directorio si no existe
    directorio = f"resultados/{user_id}"
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    # Crear el nombre del archivo basado en la fecha y hora actual
    archivo = f"{directorio}/resultado_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Guardar los resultados en el archivo JSON
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)

# Nuevas funciones para clasificación y regresión
@router.post("/clasificar")
async def clasificar_datos(request: AnalisisRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    table_name = request.table_name
    column_name = request.column_name

    # Obtener los datos de la tabla seleccionada
    query = text(f"SELECT * FROM {table_name}")
    df = pd.read_sql(query, db.bind)

    # Limpiar los datos
    df = limpiar_datos(df)

    # Verificar si la columna seleccionada existe
    if column_name not in df.columns:
        raise HTTPException(status_code=400, detail=f"La columna '{column_name}' no existe en la tabla '{table_name}'.")

    # Preparar los datos para la clasificación
    X = df.drop(columns=[column_name])
    y = df[column_name]

    # Convertir variables categóricas y de tipo objeto a numéricas
    X = pd.get_dummies(X, drop_first=True)

      # Asegurarse de que todas las columnas sean numéricas
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].astype('category').cat.codes

    # Verificar si hay columnas con tipos incompatibles
    tipos_invalidos = X.select_dtypes(exclude=[np.number])
    if not tipos_invalidos.empty:
        logging.warning(f"Las siguientes columnas no son numéricas y serán eliminadas: {list(tipos_invalidos.columns)}")
        X = X.drop(columns=tipos_invalidos.columns)

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Aplicar Logistic Regression para clasificación
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Calcular la precisión del modelo
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Precisión del modelo de clasificación: {accuracy}")

    resultados = {
        "user_id": current_user.usuario,
        "table_name": table_name,
        "column_name": column_name,
        "accuracy": accuracy,
        "predicciones": y_pred.tolist()
    }

    # Guardar los resultados en un archivo JSON
    guardar_resultados_json(current_user.usuario, resultados)

    return resultados

@router.post("/regresion")
async def regresion_datos(request: AnalisisRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    table_name = request.table_name
    column_name = request.column_name

    # Obtener los datos de la tabla seleccionada
    query = text(f"SELECT * FROM {table_name}")
    df = pd.read_sql(query, db.bind)

    # Limpiar los datos
    df = limpiar_datos(df)

    # Verificar si la columna seleccionada existe
    if column_name not in df.columns:
        raise HTTPException(status_code=400, detail=f"La columna '{column_name}' no existe en la tabla '{table_name}'.")

    # Preparar los datos para la regresión
    X = df.drop(columns=[column_name])
    y = df[column_name]

    # Convertir variables categóricas a numéricas
    X = pd.get_dummies(X, drop_first=True)

    # Asegurarse de que todas las columnas sean numéricas
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].astype('category').cat.codes

    # Verificar si hay columnas con tipos incompatibles
    tipos_invalidos = X.select_dtypes(exclude=[np.number])
    if not tipos_invalidos.empty:
        logging.warning(f"Las siguientes columnas no son numéricas y serán eliminadas: {list(tipos_invalidos.columns)}")
        X = X.drop(columns=tipos_invalidos.columns)

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Aplicar Linear Regression para regresión
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Calcular el error cuadrático medio del modelo
    mse = mean_squared_error(y_test, y_pred)
    logging.info(f"Error cuadrático medio del modelo de regresión: {mse}")

    resultados = {
        "user_id": current_user.usuario,
        "table_name": table_name,
        "column_name": column_name,
        "mse": mse,
        "predicciones": y_pred.tolist()
    }

    # Guardar los resultados en un archivo JSON
    guardar_resultados_json(current_user.usuario, resultados)

    return resultados

def limpiar_datos(df):
    # Eliminar duplicados
    df = df.drop_duplicates()

    # Resetear el índice después de eliminar filas duplicadas
    df.reset_index(drop=True, inplace=True)

    # Convertir columnas de fecha a tipo datetime y luego a números
    columnas_fecha = [col for col in df.columns if 'fecha' in col.lower()]
    for col in columnas_fecha:
        if col in df.columns:
            # Convertir a datetime
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # Extraer características de fecha si lo deseas
            df[col + '_year'] = df[col].dt.year
            df[col + '_month'] = df[col].dt.month
            df[col + '_day'] = df[col].dt.day
            # O convertir a timestamp
            df[col + '_timestamp'] = df[col].apply(lambda x: x.timestamp() if pd.notnull(x) else np.nan)
            # Eliminar la columna original de fecha
            df.drop(columns=[col], inplace=True)

    # Manejar valores nulos
    df = df.dropna()

    return df