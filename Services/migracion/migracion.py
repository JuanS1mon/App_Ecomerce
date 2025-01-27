# Services/migracion/migracion.py
import os
import logging
import pandas as pd
from io import BytesIO
import json
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, BigInteger
from db.models.activityLog import ActivityLog
from db.models.usuarios import usuarios
from typing import List, Dict, Any, Union

# Funciones de utilidad
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

def verificar_no_datetime(data, context=""):
    """Función para verificar y registrar si hay objetos datetime en los datos."""
    for idx, record in enumerate(data):
        for key, value in record.items():
            if isinstance(value, datetime):
                logging.error(f"Objeto datetime encontrado en {context}, registro {idx}, campo {key}: {value}")
                record[key] = value.strftime('%Y-%m-%d %H:%M:%S')

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

def determinar_tipo_predominante(data: List[Dict[str, Any]]) -> Dict[str, Union[type, str]]:
    """
    Determina el tipo de datos predominante para cada columna en una lista de diccionarios.
    
    Parámetros:
        data (List[Dict[str, Any]]): Lista de registros a analizar.
    
    Retorna:
        Dict[str, Union[type, str]]: Diccionario con el tipo de datos predominante para cada columna.
    """
    tipo_predominante = {}
    for key in data[0].keys():
        tipos = [type(record[key]) for record in data if record[key] is not None]
        if not tipos:
            tipo_predominante[key] = str
        else:
            tipo_mas_comun = max(set(tipos), key=tipos.count)
            if tipo_mas_comun in [int, float]:
                tipo_predominante[key] = int if tipos.count(int) > tipos.count(float) else float
            elif tipo_mas_comun == datetime:
                tipo_predominante[key] = 'datetime'
            else:
                tipo_predominante[key] = str
    return tipo_predominante

def limpiar_datos(data: List[Dict[str, Any]], esquema_tipos: Dict[str, Union[type, str]]) -> List[Dict[str, Any]]:
    """
    Limpia y valida los datos de una lista de diccionarios según el esquema definido.
    
    Parámetros:
        data (List[Dict[str, Any]]): Lista de registros a limpiar.
        esquema_tipos (Dict[str, Union[type, str]]): Diccionario con el tipo de datos predominante para cada columna.
    
    Retorna:
        List[Dict[str, Any]]: Lista de registros limpios.
    """
    registros_limpios = []
    registros_invalidos = []
    
    for idx, record in enumerate(data):
        limpio = {}
        registro_valido = True  # Flag para determinar si el registro es válido
        
        for key, expected_type in esquema_tipos.items():
            value = record.get(key, None)
            try:
                if pd.isna(value):
                    limpio[key] = None
                elif expected_type == int:
                    limpio[key] = int(value)
                elif expected_type == float:
                    limpio[key] = float(value)
                elif expected_type == 'datetime':
                    if isinstance(value, (pd.Timestamp, datetime)):
                        limpio[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        limpio[key] = pd.to_datetime(value).strftime('%Y-%m-%d %H:%M:%S')
                elif expected_type == str:
                    limpio[key] = value.strip() if isinstance(value, str) else str(value).strip()
                else:
                    limpio[key] = str(value).strip()
            except (ValueError, TypeError) as e:
                logging.error(f"Error en registro {idx}, campo '{key}': {e}")
                limpio[key] = None
                registro_valido = False
        
        registros_limpios.append(limpio)
        
        if not registro_valido:
            registros_invalidos.append(limpio)
    
    if registros_invalidos:
        invalid_json_path = f"logs/invalidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(invalid_json_path, 'w', encoding='utf-8') as f:
                json.dump(registros_invalidos, f, ensure_ascii=False, indent=4)
            logging.warning(f"Se encontraron {len(registros_invalidos)} registros inválidos. Ver archivo: {invalid_json_path}")
        except Exception as e:
            logging.error(f"Error al guardar registros inválidos: {e}")
    
    return registros_limpios

def procesar_archivo(sheet_json_path, result_path, db: Session, current_user: usuarios, table_name: str):
    try:
        # Leer los datos del archivo JSON
        with open(sheet_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validar que los datos no estén vacíos
        if not data:
            logging.error(f"El archivo JSON {sheet_json_path} no contiene datos.")
            result = {
                "status": "error",
                "message": "El archivo JSON no contiene datos."
            }
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4, default=str)
            return
        
        # Contador de registros originales
        total_registros = len(data)
        
        # Determinar el tipo predominante de cada columna
        esquema_tipos = determinar_tipo_predominante(data)
        
        # Limpiar y validar datos
        data = limpiar_datos(data, esquema_tipos)
        
        # Verificar no hay datetime
        verificar_no_datetime(data, context="después de limpiar_datos")
        
        # Inicializar contadores
        registros_no_guardados = []
        registros_procesados = 0
        
        # Procesar EAN si existe
        if any('EAN' in record for record in data):
            # Procesar EAN en cada registro
            for record in data:
                if 'EAN' in record:
                    try:
                        # Intentar convertir EAN a número
                        record['EAN'] = int(float(record['EAN']))
                    except:
                        registros_no_guardados.append(record)
                        continue
        
            # Filtrar registros válidos
            data = [record for record in data if 'EAN' in record]
        
            # Modificar EAN
            for record in data:
                record['EAN_MODIFICADO'] = modificar_ean(record['EAN'])
        
            # Filtrar registros con EAN inválidos
            registros_ean_invalidos = [record for record in data if record['EAN_MODIFICADO'] is None]
            registros_no_guardados.extend(registros_ean_invalidos)
            data = [record for record in data if record['EAN_MODIFICADO'] is not None]
        
            # Actualizar EAN y eliminar campo temporal
            for record in data:
                record['EAN'] = record['EAN_MODIFICADO']
                del record['EAN_MODIFICADO']
        
        # Convertir valores numéricos si es posible
        for record in data:
            for key, value in record.items():
                if isinstance(value, float):
                    record[key] = convertir_a_float(value)
                elif isinstance(value, int):
                    record[key] = convertir_a_int(value)
        
        # Verificar nuevamente
        verificar_no_datetime(data, context="después de convertir valores numéricos")
        
        # Crear tabla dinámica
        metadata = MetaData()
        columns = [Column('id', BigInteger, primary_key=True, autoincrement=True)]
        
        if not data:
            logging.error("No hay datos válidos para insertar.")
            result = {
                "status": "error",
                "message": "No hay datos válidos para insertar."
            }
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4, default=str)
            return
        
        # Asumiendo que todos los registros tienen las mismas claves
        first_record = data[0]
        for column_name, value in first_record.items():
            # Determinar el tipo de columna basado en el valor de los datos
            if column_name == 'EAN':
                column_type = BigInteger
            elif column_name in ['Codigo_DUN', 'Cantidad_DUN']:
                column_type = BigInteger
            else:
                # Mapeo basado en el tipo en los datos
                if isinstance(value, int):
                    column_type = BigInteger
                elif isinstance(value, float):
                    column_type = Float
                elif isinstance(value, bool):
                    column_type = Boolean
                elif isinstance(value, str):
                    column_type = String
                else:
                    column_type = String  # Por defecto
            
            columns.append(Column(column_name, column_type))
        
        # Crear la tabla
        dynamic_table = Table(table_name, metadata, *columns)
        metadata.create_all(db.get_bind(), tables=[dynamic_table])
        
        # Insertar datos
        for record in data:
            try:
                db.execute(dynamic_table.insert(), record)
                registros_procesados += 1
            except Exception as e:
                logging.error(f"Error al insertar registro: {str(e)}")
                registros_no_guardados.append(record)
        
        # Guardar registros no válidos
        if registros_no_guardados:
            # Verificar si hay datetime en registros_no_guardados
            verificar_no_datetime(registros_no_guardados, context="registros_no_guardados")
            
            invalid_json_path = os.path.join(os.path.dirname(sheet_json_path), f"invalidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(invalid_json_path, 'w', encoding='utf-8') as f:
                json.dump(registros_no_guardados, f, ensure_ascii=False, indent=4, default=str)
            
            logging.warning(f"Registros no guardados: {len(registros_no_guardados)}")
        
        # Calcular porcentaje de registros cargados
        porcentaje_cargados = (registros_procesados / total_registros) * 100 if total_registros > 0 else 0
        
        # Log del resultado
        logging.info(f"Migración completada: {registros_procesados} registros procesados, {len(registros_no_guardados)} registros inválidos, {porcentaje_cargados:.2f}% de registros cargados")
        
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
            "message": f"Migración completada: {registros_procesados} registros procesados, {len(registros_no_guardados)} registros inválidos, {porcentaje_cargados:.2f}% de registros cargados"
        }
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4, default=str)

    except Exception as e:
        logging.error(f"Ocurrió un error al procesar el archivo: {str(e)}")
        result = {
            "status": "error",
            "message": f"Ocurrió un error al procesar el archivo: {str(e)}"
        }
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4, default=str)