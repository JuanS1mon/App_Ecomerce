import datetime
from typing import Any, List, Dict
import pandas as pd
import numpy as np
import json
import os
from sqlalchemy.orm import Session
from ...db.models.resultados import ResultadoKPI

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
            # Especificar el formato de la fecha si es conocido
            try:
                df[col] = pd.to_datetime(df[col], format='%Y-%m-%d', errors='coerce')
            except ValueError:
                df[col] = pd.to_datetime(df[col], errors='coerce')

    return df

def convert_types(obj):
    """
    Convierte objetos complejos (pandas Timestamp, datetime, etc) a formatos serializables
    """
    if obj is None:
        return None
    elif isinstance(obj, (pd.Timestamp, datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_types(i) for i in obj]
    elif isinstance(obj, pd.Series):
        return convert_types(obj.to_dict())
    elif isinstance(obj, pd.DataFrame):
        return convert_types(obj.to_dict(orient="records"))
    elif hasattr(obj, "__str__"):
        return str(obj)
    return obj

def guardar_resultados_sql(db: Session, usuario: str, resultados: Dict[str, Any]):
    """
    Guarda los resultados del análisis KPI en la base de datos.
    
    Args:
        db: Sesión de base de datos
        usuario: Nombre de usuario que realizó el análisis
        resultados: Diccionario con los resultados del análisis
    """
    try:
        # Verificar si el usuario es válido
        if not usuario:
            print("Error: Nombre de usuario no válido")
            return
        
        # Crear un nuevo registro utilizando ResultadoKPI
        nuevo_analisis = ResultadoKPI(
            usuario=usuario,
            total_registros=resultados.get("total_registros"),
            categorias=resultados.get("categorias"),
            last_date=resultados.get("last_date"),
            first_date=resultados.get("first_date"),
            max_value=resultados.get("max_value"),
            min_value=resultados.get("min_value"),
            clusters=resultados.get("clusters")
        )
        
        # Agregar y guardar en la base de datos
        db.add(nuevo_analisis)
        db.commit()
        print(f"Resultados guardados para el usuario {usuario}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error al guardar resultados: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
    
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