from typing import List, Dict
import pandas as pd
import numpy as np
import json
import os
from sqlalchemy.orm import Session
from db.models.resultados import ResultadoKPI

def clean_data(data: List[Dict]) -> List[Dict]:
    """
    Función para limpiar datos duplicados.
    """
    seen = set()
    cleaned_data = []
    for item in data:
        tuple_item = tuple(item.items())
        if tuple_item not in seen:
            seen.add(tuple_item)
            cleaned_data.append(item)
    return cleaned_data

def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función para limpiar un DataFrame eliminando duplicados y convirtiendo columnas de fecha.
    """
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
            # df[col + '_year'] = df[col].dt.year
            # df[col + '_month'] = df[col].dt.month
            # df[col + '_day'] = df[col].dt.day

    return df

def convert_types(obj):
    """
    Función para convertir tipos de datos no serializables a tipos serializables.
    """
    if isinstance(obj, np.int64):
        return int(obj)
    if isinstance(obj, np.float64):
        return float(obj)
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def guardar_resultados_sql(db: Session, usuario: str, resultados: Dict):
    """
    Función para guardar los resultados en la base de datos.
    """
    try:
        # Convertir clusters a string si es necesario
        clusters_str = json.dumps(resultados.get("clusters", []))

        resultado_kpi = ResultadoKPI(
            usuario=usuario,
            total_registros=int(resultados.get("total_registros", 0)),
            categorias=int(resultados.get("categorias", 0)),
            last_date=pd.to_datetime(resultados.get("last_date")).to_pydatetime() if resultados.get("last_date") else None,
            first_date=pd.to_datetime(resultados.get("first_date")).to_pydatetime() if resultados.get("first_date") else None,
            max_value=float(resultados.get("max_value", 0)),
            min_value=float(resultados.get("min_value", 0)),
            clusters=clusters_str
        )

        db.add(resultado_kpi)
        db.commit()
        db.refresh(resultado_kpi)
    except Exception as e:
        db.rollback()
        raise e

def guardar_resultados_json(usuario: str, resultados: Dict):
    """
    Función para guardar los resultados en un archivo JSON.
    """
    try:
        # Crear el directorio si no existe
        directorio = f"resultados/{usuario}"
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        # Guardar los resultados en un archivo JSON
        with open(f"{directorio}/resultados.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4, default=convert_types)
    except Exception as e:
        raise e