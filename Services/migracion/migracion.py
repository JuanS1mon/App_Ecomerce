import pandas as pd
from sqlalchemy import create_engine
import re

def importar_datos_desde_xls(ruta_archivo):
    # Leer el archivo .xls
    df = pd.read_excel(ruta_archivo)

    # Convertir columnas a los tipos correctos
    df['EAN'] = pd.to_numeric(df['EAN'], errors='coerce')
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
    df['costo'] = pd.to_numeric(df['costo'], errors='coerce')
    df['IVA'] = pd.to_numeric(df['IVA'], errors='coerce')

    # Eliminar filas con datos faltantes esenciales
    df = df.dropna(subset=['codigo', 'Nombre','EAN'])

    # Rellenar valores NaN con valores por defecto si es necesario
    df = df.fillna({'EAN': 0, 'precio': 0.0, 'costo': 0.0, 'IVA': 0.0})

    # Quitar caracteres especiales de la columna 'descripcion'
    df['descripcion'] = df['descripcion'].apply(lambda x: re.sub(r'[^A-Za-z0-9\s]+', '', str(x)))

    # Eliminar el dígito verificador del EAN
    df['EAN'] = df['EAN'].apply(lambda x: str(x)[:-1] if len(str(x)) in [8, 13, 14] else str(x))

    # Eliminar filas con EAN no válidos
    df = df.dropna(subset=['EAN'])

    # Crear conexión a la base de datos
    engine = create_engine('postgresql://usuario:contraseña@localhost/base_de_datos')

    # Insertar los datos en la tabla 'articulos'
    try:
        df.to_sql('m_articulos', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"Error al insertar datos en la base de datos: {e}")

# Ejemplo de uso
importar_datos_desde_xls('ruta/al/archivo.xls')