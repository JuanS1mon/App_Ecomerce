# Services/migracion/migracion.py
import os
import logging
import pandas as pd
from io import BytesIO
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, BigInteger
from db.models.activityLog import ActivityLog
from db.models.usuarios import usuarios

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
        
def procesar_archivo(contents, json_path, result_path, db: Session, current_user, table_name):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(BytesIO(contents))

        # Validar que el DataFrame no esté vacío
        if df.empty:
            logging.error("El archivo Excel no contiene datos.")
            result = {
                "status": "error",
                "message": "El archivo Excel no contiene datos."
            }
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            return

        # Convertir DataFrame a una lista de diccionarios
        data = df.to_dict(orient='records')

        # Guardar datos en un archivo JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logging.info("Archivo procesado y datos guardados exitosamente en formato JSON.")

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
            elif column_name in ['Codigo_DUN', 'Cantidad_DUN']:
                column_type = BigInteger  # Ajustar para valores grandes
            else:
                column_type = type_mapping.get(pandas_type, String)
            columns.append(Column(column_name, column_type))

        # Crear tabla
        dynamic_table = Table(table_name, metadata, *columns)
        metadata.create_all(db.get_bind(), tables=[dynamic_table])

        # Insertar datos
        records = df.to_dict(orient='records')
        registros_procesados = 0
        
        for record in records:
            try:
                db.execute(dynamic_table.insert(), [record])
                registros_procesados += 1
            except Exception as e:
                logging.error(f"Error al insertar registro: {str(e)}")
                registros_no_guardados.append(record)

        # Guardar registros no válidos
        if registros_no_guardados:
            invalid_json_path = os.path.join(os.path.dirname(json_path), f"invalidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(invalid_json_path, 'w', encoding='utf-8') as f:
                json.dump(registros_no_guardados, f, ensure_ascii=False, indent=4)
            
            logging.warning(f"Registros no guardados: {len(registros_no_guardados)}")

        # Calcular porcentaje de registros cargados
        porcentaje_cargados = (registros_procesados / total_registros) * 100

        # Log del resultado
        logging.info(f"Migración completada: {registros_procesados} registros procesados, "
                    f"{len(registros_no_guardados)} registros inválidos, "
                    f"{porcentaje_cargados:.2f}% de registros cargados")

        # Buscar el usuario por nombre de usuario
        usuario = db.query(usuarios).filter(usuarios.usuario == current_user.usuario).first()
        if not usuario:
            logging.error("Usuario no encontrado")
            raise Exception("Usuario no encontrado")

        # Registrar la actividad
        new_activity = ActivityLog(
            usuario_id=usuario.codigo,
            action=f"Realizó una migración de datos el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        db.add(new_activity)
        db.commit()

        # Guardar resultado
        result = {
            "status": "success",
            "message": f"Migración completada: {registros_procesados} registros procesados, "
                       f"{len(registros_no_guardados)} registros inválidos, "
                       f"{porcentaje_cargados:.2f}% de registros cargados"
        }
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error(f"Ocurrió un error al procesar el archivo: {str(e)}")
        result = {
            "status": "error",
            "message": f"Ocurrió un error al procesar el archivo: {str(e)}"
        }
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)