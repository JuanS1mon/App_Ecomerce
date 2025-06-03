import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from .mdb_service import mdb_service
import pyodbc
import json
import traceback

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Verificar si ya existe un handler para evitar duplicar logs
if not logger.handlers:
    handler = logging.FileHandler('logs/mdb_sync.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Agregar también un console handler para ver logs en la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Mapeo predeterminado para tablas comunes
DEFAULT_TABLE_MAPPINGS = {
    'articulos': {
        'mdb_table': 'Productos',
        'columns': {
            'id': 'ID',
            'codigo': 'Codigo',
            'descripcion': 'Descripcion',
            'preciocosto': 'PrecioCompra',
            'marca': 'Marca'
        }
    },
    'clientes': {
        'mdb_table': 'Clientes',
        'columns': {
            'id': 'ID',
            'razon_social': 'Nombre',
            'numero_documento': 'Documento',
            'direccion': 'Direccion',
            'telefono': 'Telefono',
            'email': 'Email'
        }
    },
    'promociones': {
        'mdb_table': 'Promociones',
        'columns': {
            'id': 'ID',
            'nombre': 'Descripcion',
            'fecha_inicio': 'FechaInicio',
            'fecha_fin': 'FechaFin',
            'descuento': 'Descuento'
        }
    }
}

def setup_mdb_connection(mdb_path: str = None, ip: str = None, port: int = 9933) -> bool:
    """
    Configura la conexión con el archivo MDB
    
    Args:
        mdb_path: Ruta al archivo MDB (local o red)
        ip: Dirección IP para transmisión de datos (opcional)
        port: Puerto para la transmisión (por defecto 9933)
        
    Returns:
        bool: Éxito de la operación
    """
    if ip:
        mdb_service.set_remote_connection(ip, port)
        # Probar conexión por socket
        success, message = mdb_service.test_socket_connection()
        if not success:
            logger.warning(f"Advertencia en conexión socket: {message}")
    
    if mdb_path:
        mdb_service.set_path(mdb_path)
        
    # Conectar al archivo MDB
    return mdb_service.connect()

def setup_table_mappings(custom_mappings: Dict[str, Dict] = None) -> None:
    """
    Configura los mapeos entre tablas SQL y MDB
    
    Args:
        custom_mappings: Mapeos personalizados que sobrescribirán los predeterminados
    """
    # Usar mapeos predeterminados
    mappings = DEFAULT_TABLE_MAPPINGS.copy()
    
    # Aplicar mapeos personalizados si existen
    if custom_mappings:
        for table, mapping in custom_mappings.items():
            if table in mappings:
                # Actualizar mapeo existente
                if 'mdb_table' in mapping:
                    mappings[table]['mdb_table'] = mapping['mdb_table']
                if 'columns' in mapping:
                    mappings[table]['columns'].update(mapping['columns'])
            else:
                # Agregar nuevo mapeo
                mappings[table] = mapping
    
    # Configurar los mapeos en el servicio
    for sql_table, details in mappings.items():
        mdb_service.map_tables(
            sql_table=sql_table,
            mdb_table=details['mdb_table'],
            column_mappings=details['columns']
        )

def sync_tables_to_mdb(db: Session, 
                       mdb_path: str = None, 
                       ip: str = None, 
                       port: int = 9933,
                       custom_mappings: Dict = None, 
                       tables: List[str] = None) -> Dict[str, Any]:
    """
    Sincroniza tablas SQL a un archivo MDB
    
    Args:
        db: Sesión de base de datos SQLAlchemy
        mdb_path: Ruta al archivo MDB (local o red)
        ip: Dirección IP para transmisión de datos (opcional)
        port: Puerto para la transmisión (por defecto 9933)
        custom_mappings: Mapeos personalizados para las tablas
        tables: Lista de tablas a sincronizar (None = todas las mapeadas)
        
    Returns:
        Dict: Resultados de la sincronización
    """
    start_time = datetime.now()
    results = {
        "success": False,
        "timestamp": start_time.isoformat(),
        "mdb_path": mdb_path,
        "ip_address": ip,
        "port": port,
        "tables_processed": [],
        "errors": []
    }
    
    try:
        # Configurar la conexión
        connected = setup_mdb_connection(mdb_path, ip, port)
        if not connected:
            results["errors"].append("No se pudo conectar al archivo MDB")
            return results
        
        # Configurar los mapeos de tablas
        setup_table_mappings(custom_mappings)
        
        # Determinar qué tablas sincronizar
        tables_to_sync = tables if tables else list(DEFAULT_TABLE_MAPPINGS.keys())
        
        # Sincronizar cada tabla
        for table in tables_to_sync:
            try:
                table_result = mdb_service.sync_table(db, table)
                results["tables_processed"].append({
                    "table": table,
                    "success": table_result["success"],
                    "records": table_result.get("records_count", 0)
                })
                if not table_result["success"]:
                    results["errors"].append(f"Error al sincronizar {table}: {table_result.get('error', 'Error desconocido')}")
            except Exception as e:
                results["errors"].append(f"Error al procesar {table}: {str(e)}")
        
        # Actualizar el estado final
        results["success"] = len(results["errors"]) == 0
        results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
        
    except Exception as e:
        results["errors"].append(f"Error general: {str(e)}")
    
    finally:
        # Cerrar la conexión
        try:
            mdb_service.disconnect()
        except:
            pass
            
    return results

def get_mdb_table_info(mdb_path: str) -> Dict[str, Any]:
    """
    Obtiene información sobre las tablas en un archivo MDB
    
    Args:
        mdb_path: Ruta al archivo MDB
        
    Returns:
        Dict: Información de las tablas
    """
    try:
        # Configurar la conexión
        mdb_service.set_path(mdb_path)
        if not mdb_service.connect():
            return {"success": False, "error": "No se pudo conectar al archivo MDB"}
        
        # Obtener lista de tablas
        tables = mdb_service.list_tables()
        
        # Obtener estructura de cada tabla
        tables_info = {}
        for table in tables:
            try:
                structure = mdb_service.get_table_structure(table)
                sample_data = mdb_service.read_table(table, limit=5)
                
                tables_info[table] = {
                    "columns": structure,
                    "row_count": len(sample_data) if not sample_data.empty else 0,
                    "sample_data": sample_data.head(5).to_dict(orient="records") if not sample_data.empty else []
                }
            except Exception as e:
                tables_info[table] = {
                    "error": str(e)
                }
        
        return {
            "success": True,
            "file_path": mdb_path,
            "tables_count": len(tables),
            "tables": tables_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        mdb_service.disconnect()

# Nueva función para sincronizar específicamente artículos con MDB
def sync_articulos_to_mdb(db: Session, mdb_path: str, ip: str = None, port: int = 9933) -> Dict[str, Any]:
    """
    Sincroniza artículos de SQL a la tabla de artículos en MDB con el formato solicitado
    
    Args:
        db: Sesión de base de datos SQLAlchemy
        mdb_path: Ruta al archivo MDB (local o red)
        ip: Dirección IP para transmisión de datos (opcional)
        port: Puerto para la transmisión (por defecto 9933)
        
    Returns:
        Dict: Resultados de la sincronización
    """
    start_time = datetime.now()
    results = {
        "success": False,
        "timestamp": start_time.isoformat(),
        "mdb_path": mdb_path,
        "ip_address": ip,
        "port": port,
        "records_processed": 0,
        "error": None
    }
    
    try:
        # Configurar la conexión
        connected = setup_mdb_connection(mdb_path, ip, port)
        if not connected:
            results["error"] = "No se pudo conectar al archivo MDB"
            return results
        
        # Obtener datos de artículos desde la base de datos SQL
        query = """
            SELECT id, codigo, descripcion, preciocosto, precio_venta
            FROM articulos
        """
        
        result = db.execute(text(query))
        rows = result.fetchall()
        
        if not rows:
            results["error"] = "No se encontraron artículos para sincronizar"
            return results
        
        # Crear DataFrame con los datos obtenidos
        articulos_df = pd.DataFrame(rows, columns=['id', 'codigo', 'descripcion', 'precio_costo', 'precio_venta'])
        
        # Crear DataFrame para la tabla de artículos en MDB con el formato solicitado
        mdb_articulos = pd.DataFrame()
        mdb_articulos['EAN'] = articulos_df['codigo']
        mdb_articulos['Descripcion'] = articulos_df['descripcion']
        mdb_articulos['DescripcionCorta'] = articulos_df['descripcion']
        mdb_articulos['Tipo'] = "N"  # Valor fijo según lo solicitado
        mdb_articulos['Precio1'] = articulos_df['precio_venta']
        mdb_articulos['Precio2'] = articulos_df['precio_venta']
        mdb_articulos['EsEnvase'] = 0  # Valor fijo según lo solicitado
        mdb_articulos['Envase'] = 0    # No especificado en los requisitos, asumimos 0
        mdb_articulos['Acumulador'] = 1  # Valor fijo según lo solicitado
        mdb_articulos['Iva'] = 21       # Valor fijo según lo solicitado
        mdb_articulos['ImpInt'] = 0     # Valor fijo según lo solicitado
        
        # Escribir los datos en la tabla de artículos del archivo MDB
        success = mdb_service.write_to_mdb(mdb_articulos, 'articulos')
        
        results["success"] = success
        results["records_processed"] = len(mdb_articulos)
        results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
        
    except Exception as e:
        results["error"] = str(e)
        logger.error(f"Error al sincronizar artículos a MDB: {e}")
    
    finally:
        # Cerrar la conexión
        try:
            mdb_service.disconnect()
        except:
            pass
            
    return results

# Nueva función de prueba para verificar la conexión y el envío de datos
def test_mdb_connection(mdb_path: str, ip: str = None, port: int = 9933) -> Dict[str, Any]:
    """
    Función de prueba para verificar la conexión al archivo MDB y validar la ruta
    
    Args:
        mdb_path: Ruta al archivo MDB (local o red)
        ip: Dirección IP para transmisión de datos (opcional)
        port: Puerto para la transmisión (por defecto 9933)
        
    Returns:
        Dict: Resultados de la prueba
    """
    import os
    
    results = {
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "mdb_path": mdb_path,
        "ip_address": ip,
        "port": port,
        "file_exists": None,
        "connection_test": None,
        "errors": []
    }
    
    print(f"[TEST] Probando conexión a MDB: {mdb_path}")
    
    # Verificar si el archivo existe
    if mdb_path:
        file_exists = os.path.isfile(mdb_path)
        results["file_exists"] = file_exists
        print(f"[TEST] ¿El archivo existe? {file_exists}")
        
        if not file_exists:
            results["errors"].append(f"El archivo MDB no existe en la ruta: {mdb_path}")
    else:
        results["errors"].append("No se proporcionó una ruta de archivo MDB")
    
    # Probar conexión al archivo MDB
    try:
        print(f"[TEST] Configurando conexión MDB...")
        connected = setup_mdb_connection(mdb_path, ip, port)
        results["connection_test"] = connected
        print(f"[TEST] ¿Conexión exitosa? {connected}")
        
        if connected:
            print("[TEST] Listando tablas disponibles...")
            tables = mdb_service.list_tables()
            results["tables"] = tables
            results["tables_count"] = len(tables)
            print(f"[TEST] Tablas encontradas: {len(tables)}")
            
            results["success"] = True
        else:
            results["errors"].append("No se pudo conectar al archivo MDB")
            
    except Exception as e:
        error_msg = f"Error al probar conexión MDB: {str(e)}"
        results["errors"].append(error_msg)
        print(f"[TEST] {error_msg}")
    
    finally:
        # Cerrar la conexión
        try:
            mdb_service.disconnect()
            print("[TEST] Conexión cerrada")
        except:
            pass
    
    # Imprimir resumen
    if results["success"]:
        print(f"[TEST] Prueba exitosa - Archivo: {mdb_path} - Tablas: {results.get('tables_count', 0)}")
    else:
        print(f"[TEST] Prueba fallida - Errores: {results['errors']}")
    
    return results

def send_generic_article_test(mdb_path: str, ip: str = None, port: int = 9933) -> Dict[str, Any]:
    """
    Función para enviar un artículo genérico de prueba al archivo MDB.
    Esto es útil para verificar la conexión y escritura sin depender de la base de datos SQL.
    
    Args:
        mdb_path: Ruta al archivo MDB (local o red)
        ip: Dirección IP para transmisión de datos (opcional)
        port: Puerto para la transmisión (por defecto 9933)
        
    Returns:
        Dict: Resultados de la prueba
    """
    import os
    import pandas as pd
    from datetime import datetime
    
    start_time = datetime.now()
    results = {
        "success": False,
        "timestamp": start_time.isoformat(),
        "mdb_path": mdb_path,
        "ip_address": ip,
        "port": port,
        "file_exists": None,
        "connection_test": None,
        "write_test": None,
        "errors": []
    }
    
    print(f"[TEST] Iniciando prueba con artículo genérico para MDB: {mdb_path}")
    
    # Verificar si el archivo existe
    if mdb_path:
        file_exists = os.path.isfile(mdb_path)
        results["file_exists"] = file_exists
        print(f"[TEST] ¿El archivo existe? {file_exists}")
        
        if not file_exists:
            results["errors"].append(f"El archivo MDB no existe en la ruta: {mdb_path}")
            return results
    else:
        results["errors"].append("No se proporcionó una ruta de archivo MDB")
        return results
    
    # Probar conexión al archivo MDB
    try:
        print(f"[TEST] Configurando conexión MDB...")
        connected = setup_mdb_connection(mdb_path, ip, port)
        results["connection_test"] = connected
        print(f"[TEST] ¿Conexión exitosa? {connected}")
        
        if not connected:
            results["errors"].append("No se pudo conectar al archivo MDB")
            return results
            
        # Crear un artículo genérico de prueba
        print("[TEST] Creando datos de artículo genérico...")
        
        # Crear DataFrame con un artículo de prueba
        generic_article = pd.DataFrame([{
            "EAN": "123456789",
            "Descripcion": "ARTÍCULO DE PRUEBA",
            "DescripcionCorta": "PRUEBA",
            "Tipo": "N",
            "Precio1": 100.50,
            "Precio2": 120.75,
            "EsEnvase": 0,
            "Envase": 0,
            "Acumulador": 1,
            "Iva": 21,
            "ImpInt": 0
        }])
        
        print("[TEST] Datos de artículo genérico creados. Intentando escribir en MDB...")
        
        # Intentar escribir en diferentes tablas comunes para artículos en MDB
        tables_to_try = ["Articulos", "Productos", "Items", "articulos", "productos"]
        write_success = False
        
        for table in tables_to_try:
            try:
                print(f"[TEST] Intentando escribir en tabla '{table}'...")
                success = mdb_service.write_to_mdb(generic_article, table)
                if success:
                    write_success = True
                    results["table_used"] = table
                    print(f"[TEST] Escritura exitosa en tabla '{table}'")
                    break
            except Exception as e:
                print(f"[TEST] Error al escribir en tabla '{table}': {str(e)}")
        
        results["write_test"] = write_success
        if not write_success:
            results["errors"].append("No se pudo escribir el artículo en ninguna tabla conocida")
            
        # Resultado final
        results["success"] = connected and write_success
        results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            
    except Exception as e:
        error_msg = f"Error general: {str(e)}"
        results["errors"].append(error_msg)
        print(f"[TEST] {error_msg}")
    
    finally:
        # Cerrar la conexión
        try:
            mdb_service.disconnect()
            print("[TEST] Conexión cerrada")
        except:
            pass
    
    # Imprimir resumen
    if results["success"]:
        print(f"[TEST] Prueba exitosa - Archivo: {mdb_path} - Se escribió artículo genérico")
    else:
        print(f"[TEST] Prueba fallida - Errores: {results['errors']}")
    
    return results

def get_mdb_connection(mdb_path: str, ip_address: Optional[str] = None, port: Optional[int] = None) -> pyodbc.Connection:
    """
    Establece una conexión a la base de datos MDB, ya sea local o remota.
    
    Args:
        mdb_path: Ruta al archivo MDB
        ip_address: Dirección IP para conexión remota (opcional)
        port: Puerto para conexión remota (opcional, default 9933)
    
    Returns:
        pyodbc.Connection: Conexión a la base de datos MDB
    """
    try:
        print(f"Intentando conectar a MDB: {mdb_path}")
        
        # Verificar que exista el controlador de Access
        drivers = pyodbc.drivers()
        access_drivers = [d for d in drivers if 'Access' in d]
        
        if not access_drivers:
            error_msg = "No se encontró ningún controlador para Microsoft Access en el sistema"
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            logger.error(f"Controladores disponibles: {drivers}")
            raise RuntimeError(error_msg)
            
        # Usar el primer controlador de Access disponible
        access_driver = access_drivers[0]
        print(f"Usando controlador: {access_driver}")
        
        if ip_address:
            # Conexión remota usando formato DSN o TCP/IP directo
            port = port or 9933
            conn_str = f"DRIVER={{{access_driver}}};DBQ={mdb_path};SERVER={ip_address};PORT={port};"
            print(f"Usando conexión remota: {conn_str}")
        else:
            # Conexión local
            if not os.path.isfile(mdb_path):
                error_msg = f"El archivo MDB no existe en la ruta: {mdb_path}"
                print(f"ERROR: {error_msg}")
                raise FileNotFoundError(error_msg)
                
            conn_str = f"DRIVER={{{access_driver}}};DBQ={mdb_path};"
            print(f"Usando conexión local: {conn_str}")
        
        # Intentar conectar con configuración básica (sin opciones avanzadas)
        conn = pyodbc.connect(conn_str, autocommit=True)
        
        # Configuramos la codificación de caracteres de forma segura
        try:
            conn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
            conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
            conn.setencoding(encoding='latin1')
        except pyodbc.Error as e:
            # Si falla la configuración de codificación, lo registramos pero continuamos
            print(f"Advertencia: No se pudo configurar la codificación: {str(e)}")
            logger.warning(f"No se pudo configurar la codificación: {str(e)}")
        
        # Intentamos establecer el timeout de forma segura
        try:
            conn.timeout = 60  # 60 segundos
        except pyodbc.Error as e:
            # Si falla el timeout, lo registramos pero continuamos
            print(f"Advertencia: No se pudo configurar el timeout: {str(e)}")
            logger.warning(f"No se pudo configurar el timeout: {str(e)}")
        
        print("Conexión MDB establecida correctamente")
        return conn
    except FileNotFoundError as e:
        print(f"Error de archivo no encontrado: {str(e)}")
        logger.error(f"El archivo MDB no existe en la ruta: {mdb_path}")
        raise
    except pyodbc.Error as e:
        print(f"Error de conexión PYODBC: {str(e)}")
        logger.error(f"Error al conectar con MDB: {str(e)}")
        raise
    except Exception as e:
        print(f"Error general: {str(e)}")
        logger.error(f"Error inesperado al conectar con MDB: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def test_mdb_connection(mdb_path: str, ip_address: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Prueba la conexión a la base de datos MDB y verifica sus tablas.
    
    Args:
        mdb_path: Ruta al archivo MDB
        ip_address: Dirección IP para conexión remota (opcional)
        port: Puerto para conexión remota (opcional)
    
    Returns:
        Dict: Resultado de la prueba con información sobre las tablas
    """
    errors = []
    tables = []
    tables_count = 0
    
    try:
        print(f"Probando conexión a MDB en: {mdb_path}")
        conn = get_mdb_connection(mdb_path, ip_address, port)
        
        # Listar tablas usando métodos alternativos
        cursor = conn.cursor()
        
        try:
            # Método 1: Usar tables() del cursor ODBC (método estándar)
            cursor.tables()
            for table_info in cursor.fetchall():
                # tables() devuelve: tabla[0]=catálogo, tabla[1]=esquema, tabla[2]=nombre, tabla[3]=tipo
                if table_info[3] == 'TABLE' or table_info[3] == 'VIEW':
                    tables.append(table_info[2])
            
            print(f"Se encontraron {len(tables)} tablas usando cursor.tables()")
        except Exception as e1:
            print(f"Error al usar cursor.tables(): {str(e1)}")
            
            # Método 2: Si falla tables(), intentamos consultar tablas comunes
            try:
                common_tables = ["Articulos", "Productos", "Clientes", "Ventas", "Proveedores", 
                                "Inventario", "Items", "Products", "Customers", "Sales"]
                print(f"Buscando tablas comunes: {common_tables}")
                
                for potential_table in common_tables:
                    try:
                        # Intentar una consulta simple para verificar si la tabla existe
                        cursor.execute(f"SELECT TOP 1 * FROM [{potential_table}]")
                        tables.append(potential_table)
                        print(f"Tabla encontrada: {potential_table}")
                    except:
                        # Ignorar errores - tabla no existe
                        pass
                
                print(f"Se encontraron {len(tables)} tablas por método de prueba y error")
            except Exception as e2:
                print(f"Error al buscar tablas comunes: {str(e2)}")
                errors.append(f"No se pudieron encontrar tablas: {str(e2)}")
        
        tables_count = len(tables)
        conn.close()
        
        if tables_count > 0:
            print(f"Prueba exitosa. Se encontraron {tables_count} tablas.")
            return {
                "success": True,
                "tables_count": tables_count,
                "tables": tables[:10],  # Devolver solo las primeras 10 tablas
                "mdb_path": mdb_path,
                "remote": ip_address is not None
            }
        else:
            print("La conexión fue exitosa pero no se encontraron tablas en la base de datos.")
            return {
                "success": True,  # La conexión funcionó aunque no hay tablas
                "warning": "No se encontraron tablas en la base de datos",
                "tables_count": 0,
                "tables": [],
                "mdb_path": mdb_path,
                "remote": ip_address is not None
            }
    except Exception as e:
        error_message = f"Error al probar la conexión MDB: {str(e)}"
        print(f"ERROR: {error_message}")
        logger.error(error_message)
        logger.error(traceback.format_exc())
        errors.append(str(e))
        
        return {
            "success": False,
            "errors": errors,
            "mdb_path": mdb_path,
            "remote": ip_address is not None
        }

def send_generic_article_test(mdb_path: str, ip_address: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Envía un artículo genérico de prueba a la base de datos MDB para verificar la escritura.
    
    Args:
        mdb_path: Ruta al archivo MDB
        ip_address: Dirección IP para conexión remota (opcional)
        port: Puerto para conexión remota (opcional)
    
    Returns:
        Dict: Resultado de la operación
    """
    errors = []
    
    # Primero verificar si la conexión es válida
    connection_test = test_mdb_connection(mdb_path, ip_address, port)
    if not connection_test["success"]:
        return {
            "success": False,
            "errors": connection_test["errors"],
            "message": "No se pudo establecer conexión con el archivo MDB"
        }
    
    # Verificar si existe la tabla de artículos
    tables = connection_test.get("tables", [])
    print(f"Tablas encontradas: {tables}")
    
    # Nombres de tablas que podrían contener artículos
    possible_tables = ["Articulos", "ARTICULOS", "productos", "PRODUCTOS", "Items", "ITEMS"]
    table_used = None
    
    for table in possible_tables:
        if table in tables:
            table_used = table
            break
    
    if not table_used:
        error_msg = f"No se encontró ninguna tabla de artículos en la base de datos. Buscadas: {', '.join(possible_tables)}"
        print(f"ERROR: {error_msg}")
        return {
            "success": False,
            "errors": [error_msg],
            "tables_found": tables
        }
    
    # Datos del artículo genérico
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    generic_article = {
        "codigo": f"TEST_{current_time}",
        "descripcion": f"Artículo de prueba - {current_time}",
        "preciocosto": 100.00,
        "precioventa": 150.00,
        "stock": 1,
        "observaciones": f"Prueba de sincronización realizada el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    }
    
    try:
        conn = get_mdb_connection(mdb_path, ip_address, port)
        cursor = conn.cursor()
        
        # Intentar obtener los campos de la tabla para adaptarnos a su estructura
        cursor.execute(f"SELECT TOP 1 * FROM {table_used} WHERE 1=0")
        columns = [column[0].lower() for column in cursor.description]
        print(f"Columnas encontradas en {table_used}: {columns}")
        
        # Crear la consulta de inserción adaptada a las columnas disponibles
        fields = []
        values = []
        placeholders = []
        
        for key, value in generic_article.items():
            if key.lower() in columns:
                fields.append(key)
                values.append(value)
                placeholders.append("?")
        
        if not fields:
            error_msg = f"No se encontraron campos coincidentes en la tabla {table_used}"
            print(f"ERROR: {error_msg}")
            return {
                "success": False,
                "errors": [error_msg],
                "columns_found": columns
            }
        
        # Construir y ejecutar la consulta de inserción
        query = f"INSERT INTO {table_used} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        print(f"Ejecutando consulta: {query}")
        print(f"Valores: {values}")
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        print(f"Artículo genérico enviado correctamente a la tabla {table_used}")
        
        return {
            "success": True,
            "article": generic_article,
            "table_used": table_used,
            "fields_used": fields,
            "message": f"Artículo genérico enviado correctamente a la tabla {table_used}"
        }
    except Exception as e:
        error_message = f"Error al enviar artículo genérico: {str(e)}"
        print(f"ERROR: {error_message}")
        logger.error(error_message)
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "errors": [str(e)],
            "article": generic_article,
            "table_intended": table_used
        }

def sync_articulos_to_mdb(db: Session, mdb_path: str, ip_address: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Sincroniza los artículos de la base de datos principal con un archivo MDB.
    
    Args:
        db: Sesión de la base de datos principal
        mdb_path: Ruta al archivo MDB
        ip_address: Dirección IP para conexión remota (opcional)
        port: Puerto para conexión remota (opcional)
    
    Returns:
        Dict: Resultado de la sincronización
    """
    start_time = datetime.now()
    results = {
        "success": False,
        "timestamp": start_time.isoformat(),
        "mdb_path": mdb_path,
        "ip_address": ip_address,
        "port": port,
        "records_processed": 0,
        "errors": []
    }
    
    conn = None
    
    try:
        # Establecer una única conexión que usaremos para toda la operación
        print(f"Iniciando sincronización de artículos a MDB: {mdb_path}")
        conn = get_mdb_connection(mdb_path, ip_address, port)
        cursor = conn.cursor()
        
        # Determinar qué tablas están disponibles
        available_tables = []
        try:
            cursor.tables()
            for table_info in cursor.fetchall():
                if table_info[3] == 'TABLE' or table_info[3] == 'VIEW':
                    available_tables.append(table_info[2])
            print(f"Se encontraron {len(available_tables)} tablas en la base de datos")
        except Exception as e:
            print(f"Error al obtener lista de tablas: {str(e)}")
            results["errors"].append(f"Error al obtener tablas: {str(e)}")
            
        # Buscar la tabla de artículos
        articulos_table = None
        possible_tables = ["Articulos", "ARTICULOS", "productos", "PRODUCTOS", "Items", "ITEMS"]
        for table in possible_tables:
            if table in available_tables:
                articulos_table = table
                break
                
        if not articulos_table:
            error_msg = "No se encontró una tabla válida para artículos"
            results["errors"].append(error_msg)
            print(f"ERROR: {error_msg}")
            return results
            
        print(f"Se utilizará la tabla '{articulos_table}' para la sincronización")
        
        # Obtener estructura de la tabla para saber qué columnas tenemos disponibles
        cursor.execute(f"SELECT TOP 1 * FROM [{articulos_table}] WHERE 1=0")
        table_columns = [column[0].lower() for column in cursor.description]
        print(f"Columnas disponibles en la tabla: {table_columns}")
        
        # Obtener datos de artículos desde la base de datos SQL
        query = """
            SELECT id, codigo, descripcion, preciocosto, precio_venta
            FROM articulos
        """
        
        result = db.execute(text(query))
        rows = result.fetchall()
        
        if not rows:
            print("No se encontraron artículos para sincronizar")
            results["warning"] = "No hay artículos para sincronizar"
            results["success"] = True  # Es un éxito aunque no hay nada que sincronizar
            return results
            
        print(f"Se encontraron {len(rows)} artículos para sincronizar")
        
        # Preparar los datos adaptados a la estructura de la tabla destino
        records_processed = 0
        for row in rows:
            # Crear un diccionario con los campos disponibles
            article_data = {}
            
            # Mapeo básico de columnas - adaptamos según lo que encontramos en la tabla destino
            if 'ean' in table_columns or 'codigo' in table_columns:
                article_data['EAN' if 'ean' in table_columns else 'codigo'] = row[1]  # codigo
                
            if 'descripcion' in table_columns:
                article_data['descripcion'] = row[2]  # descripcion
                
            if 'descripcioncorta' in table_columns:
                article_data['descripcioncorta'] = row[2]  # usamos la misma descripción
                
            if 'precio1' in table_columns or 'precio' in table_columns:
                article_data['precio1' if 'precio1' in table_columns else 'precio'] = row[4]  # precio_venta
                
            if 'precio2' in table_columns:
                article_data['precio2'] = row[4]  # precio_venta
                
            if 'preciocosto' in table_columns:
                article_data['preciocosto'] = row[3]  # preciocosto
                
            # Agregar campos comunes con valores predeterminados
            common_fields = {
                'tipo': 'N',
                'esenvase': 0,
                'envase': 0,
                'acumulador': 1,
                'iva': 21,
                'impint': 0
            }
            
            # Añadir solo los campos que existen en la tabla
            for field, value in common_fields.items():
                if field in table_columns:
                    article_data[field] = value
            
            # Si no hay campos para insertar, continuar con el siguiente
            if not article_data:
                print(f"No se encontraron campos coincidentes para el artículo {row[1]}")
                continue
                
            # Construir consulta INSERT
            fields = list(article_data.keys())
            values = list(article_data.values())
            placeholders = ["?"] * len(fields)
            
            query = f"INSERT INTO [{articulos_table}] ({', '.join([f'[{f}]' for f in fields])}) VALUES ({', '.join(placeholders)})"
            
            try:
                cursor.execute(query, values)
                conn.commit()
                records_processed += 1
                
                # Imprimir progreso cada 10 registros
                if records_processed % 10 == 0:
                    print(f"Procesados {records_processed} de {len(rows)} artículos")
                    
            except Exception as e:
                print(f"Error al insertar artículo {row[1]}: {str(e)}")
                results["errors"].append(f"Error al insertar artículo {row[1]}: {str(e)}")
        
        results["records_processed"] = records_processed
        results["success"] = True
        results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
        
        print(f"Sincronización completada: {records_processed} artículos procesados en {results['duration_seconds']:.2f} segundos")
        
    except Exception as e:
        error_message = f"Error en la sincronización de artículos: {str(e)}"
        print(f"ERROR: {error_message}")
        logger.error(error_message)
        logger.error(traceback.format_exc())
        
        results["errors"].append(str(e))
        results["success"] = False
        
    finally:
        # Cerrar la conexión
        if conn:
            try:
                conn.close()
                print("Conexión cerrada")
            except:
                pass
            
    return results
