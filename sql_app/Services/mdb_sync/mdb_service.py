from datetime import datetime
import os
import logging
import pyodbc
import json
import traceback
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple

# Configuración de logging
logger = logging.getLogger("mdb_sync")
logger.setLevel(logging.INFO)

# Verificar si ya existe un manejador para evitar duplicados
if not logger.handlers:
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "logs", "mdb_sync.log")
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class MDBService:
    """Servicio para interactuar con bases de datos MDB."""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connected = False
        self.mdb_path = None
        self.connection_string = None
        self.table_mappings = {}

    def set_path(self, mdb_path: str) -> None:
        """Establece la ruta del archivo MDB"""
        self.mdb_path = mdb_path
        logger.info(f"Ruta MDB establecida: {mdb_path}")
    
    def set_remote_connection(self, ip: str, port: int = 9933) -> None:
        """Establece los datos de conexión remota"""
        self.remote_ip = ip
        self.remote_port = port
        logger.info(f"Configuración de conexión remota: IP={ip}, Puerto={port}")
    
    def test_socket_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión por socket a un servidor remoto"""
        import socket
        try:
            if not hasattr(self, 'remote_ip') or not hasattr(self, 'remote_port'):
                return False, "No se ha configurado una conexión remota"
                
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((self.remote_ip, self.remote_port))
            s.close()
            return True, f"Conexión exitosa a {self.remote_ip}:{self.remote_port}"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def map_tables(self, sql_table: str, mdb_table: str, column_mappings: Dict[str, str]) -> None:
        """
        Establece un mapeo entre tablas SQL y MDB
        
        Args:
            sql_table: Nombre de la tabla en SQL
            mdb_table: Nombre de la tabla correspondiente en MDB
            column_mappings: Diccionario con mapeo de columnas {columna_sql: columna_mdb}
        """
        self.table_mappings[sql_table] = {
            'mdb_table': mdb_table,
            'columns': column_mappings
        }
        logger.info(f"Mapeo establecido: SQL:{sql_table} -> MDB:{mdb_table}")
    
    def connect(self, mdb_path: str = None, ip_address: str = None, port: int = None) -> bool:
        """
        Establece una conexión con la base de datos MDB.
        
        Args:
            mdb_path: Ruta al archivo MDB
            ip_address: Dirección IP opcional para conexión remota
            port: Puerto opcional para conexión remota
            
        Returns:
            bool: Éxito de la conexión
        """
        try:
            # Usar mdb_path proporcionado o el guardado en el objeto
            if mdb_path:
                self.mdb_path = mdb_path
            
            if not self.mdb_path:
                logger.error("No se ha especificado una ruta para el archivo MDB")
                return False
                
            # Cerrar conexión existente si la hay
            self.disconnect()
            
            logger.info(f"Intentando conectar a MDB: {self.mdb_path}")
            
            # Detectar controladores disponibles
            drivers = pyodbc.drivers()
            access_drivers = [d for d in drivers if 'Access' in d]
            
            if not access_drivers:
                logger.error(f"No se encontró ningún controlador para Microsoft Access. Drivers disponibles: {drivers}")
                return False
                
            # Usar el primer controlador de Access disponible
            access_driver = access_drivers[0]
            logger.info(f"Usando controlador: {access_driver}")
            
            # Construir cadena de conexión
            if ip_address and port:
                # Conexión a través de TCP/IP 
                logger.info(f"Usando IP: {ip_address}, Puerto: {port}")
                self.connection_string = f"DRIVER={{{access_driver}}};DBQ={self.mdb_path};SERVER={ip_address};PORT={port};"
            else:
                # Conexión directa a archivo local
                if not os.path.exists(self.mdb_path):
                    logger.error(f"Archivo MDB no encontrado: {self.mdb_path}")
                    return False
                
                self.connection_string = f"DRIVER={{{access_driver}}};DBQ={self.mdb_path};"
                logger.debug(f"Cadena de conexión: {self.connection_string}")
            
            # Intentar conectar - sin parámetros adicionales que podrían causar problemas
            try:
                self.conn = pyodbc.connect(self.connection_string)
                
                # Configurar autocommit de forma segura
                try:
                    self.conn.autocommit = True
                except Exception as e:
                    logger.warning(f"No se pudo configurar autocommit: {str(e)}")
                
                # Intentamos configurar la codificación de caracteres de forma segura
                try:
                    self.conn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
                    self.conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
                    self.conn.setencoding(encoding='latin1')
                except Exception as e:
                    logger.warning(f"No se pudo configurar la codificación: {str(e)}")
                
                self.cursor = self.conn.cursor()
                self.connected = True
                logger.info("Conexión establecida correctamente")
                return True
            except pyodbc.Error as e:
                logger.error(f"Error de conexión ODBC: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error inesperado durante la conexión: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión con la base de datos"""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                self.cursor = None
                self.connected = False
                logger.info("Conexión cerrada correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar la conexión: {str(e)}")
    
    def list_tables(self) -> List[str]:
        """Obtiene la lista de tablas en la base de datos"""
        tables = []
        try:
            if not self.cursor or not self.connected:
                logger.error("No hay conexión activa con la base de datos")
                return []
            
            try:
                # Método 1: Usar MSysObjects (requiere permisos)
                self.cursor.execute("SELECT Name FROM MSysObjects WHERE Type=1 AND Flags=0")
                for row in self.cursor.fetchall():
                    tables.append(row[0])
                
                logger.info(f"Se encontraron {len(tables)} tablas usando MSysObjects")
            except Exception as e:
                logger.warning(f"No se pudo obtener tablas de MSysObjects: {str(e)}")
                
                # Método 2: Usar el catálogo de esquema ODBC (más compatible)
                try:
                    self.cursor.tables()
                    for row in self.cursor.fetchall():
                        # tables() devuelve: tabla[0]=catálogo, tabla[1]=esquema, tabla[2]=nombre, tabla[3]=tipo
                        if row[3] == 'TABLE' or row[3] == 'VIEW':
                            tables.append(row[2])
                    
                    logger.info(f"Se encontraron {len(tables)} tablas usando cursor.tables()")
                except Exception as e2:
                    logger.warning(f"No se pudo obtener tablas de cursor.tables(): {str(e2)}")
                    
                    # Método 3: intentar consultar una tabla conocida común en sistemas POS/Inventario
                    try:
                        common_tables = ["Articulos", "Productos", "Clientes", "Ventas", "Proveedores", 
                                        "Inventario", "Items", "Products", "Customers", "Sales"]
                        for potential_table in common_tables:
                            try:
                                # Intentar ejecutar una consulta simple que sólo devolverá 1 fila
                                self.cursor.execute(f"SELECT TOP 1 * FROM [{potential_table}]")
                                tables.append(potential_table)
                                logger.info(f"Tabla encontrada: {potential_table}")
                            except:
                                # Ignorar errores, significa que la tabla no existe
                                pass
                        
                        logger.info(f"Se encontraron {len(tables)} tablas usando el método de prueba y error")
                    except Exception as e3:
                        logger.warning(f"No se pudo obtener tablas usando el método alternativo: {str(e3)}")
            
            if not tables:
                logger.warning("No se encontraron tablas en la base de datos usando ningún método")
                
            return tables
        except Exception as e:
            logger.error(f"Error al obtener tablas: {str(e)}")
            return []
    
    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtiene la estructura de columnas de una tabla"""
        columns = []
        try:
            if not self.cursor or not self.connected:
                logger.error("No hay conexión activa con la base de datos")
                return []
            
            # Consultar la estructura de la tabla
            try:
                # Intentar con esta consulta primero
                self.cursor.execute(f"SELECT TOP 0 * FROM [{table_name}]")
                
                # Obtener información de columnas
                for column in self.cursor.description:
                    columns.append({
                        "name": column[0],
                        "type": str(column[1]),
                        "size": column[3],
                        "nullable": column[6]
                    })
                
                logger.info(f"Se encontraron {len(columns)} columnas para la tabla {table_name}")
                return columns
            except:
                # Si falla el primer intento, probar con INFORMATION_SCHEMA (accesible en algunos entornos)
                try:
                    schema_query = f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}'"
                    self.cursor.execute(schema_query)
                    
                    for row in self.cursor.fetchall():
                        columns.append({
                            "name": row[0],
                            "type": row[1],
                            "size": None,
                            "nullable": None
                        })
                    
                    logger.info(f"Se encontraron {len(columns)} columnas para la tabla {table_name} usando INFORMATION_SCHEMA")
                    return columns
                except:
                    # Último recurso: intentar seleccionar un registro y capturar la descripción
                    self.cursor.execute(f"SELECT TOP 1 * FROM [{table_name}]")
                    for column in self.cursor.description:
                        columns.append({
                            "name": column[0],
                            "type": str(column[1]),
                            "size": column[3],
                            "nullable": column[6]
                        })
                    
                    logger.info(f"Se encontraron {len(columns)} columnas para la tabla {table_name}")
                    return columns
                
        except Exception as e:
            logger.error(f"Error al obtener columnas de {table_name}: {str(e)}")
            return []
    
    def read_table(self, table_name: str, limit: int = None) -> pd.DataFrame:
        """
        Lee datos de una tabla y los devuelve como DataFrame
        
        Args:
            table_name: Nombre de la tabla
            limit: Número máximo de registros a leer (None = todos)
            
        Returns:
            pd.DataFrame con los datos
        """
        try:
            if not self.cursor or not self.connected:
                logger.error("No hay conexión activa con la base de datos")
                return pd.DataFrame()
            
            # Construir consulta
            query = f"SELECT * FROM [{table_name}]"
            if limit:
                query = f"SELECT TOP {limit} * FROM [{table_name}]"
                
            logger.info(f"Ejecutando consulta: {query}")
            
            # Leer datos con pandas
            df = pd.read_sql(query, self.conn)
            logger.info(f"Se leyeron {len(df)} filas de la tabla {table_name}")
            return df
        except Exception as e:
            logger.error(f"Error al leer tabla {table_name}: {str(e)}")
            return pd.DataFrame()
    
    def write_to_mdb(self, df: pd.DataFrame, table_name: str) -> bool:
        """
        Escribe un DataFrame en una tabla MDB
        
        Args:
            df: DataFrame con los datos a escribir
            table_name: Nombre de la tabla MDB
            
        Returns:
            bool: Éxito de la operación
        """
        if not self.cursor or not self.connected:
            logger.error("No hay conexión activa con la base de datos")
            return False
            
        try:
            # Verificar si la tabla existe
            tables = self.list_tables()
            table_exists = any(t.lower() == table_name.lower() for t in tables)
            
            if not table_exists:
                logger.warning(f"La tabla {table_name} no existe. Se intentará encontrar una tabla similar.")
                # Buscar nombre similar
                similar_tables = [t for t in tables if table_name.lower() in t.lower()]
                if similar_tables:
                    table_name = similar_tables[0]
                    logger.info(f"Se utilizará la tabla {table_name} en su lugar")
                else:
                    logger.error(f"No se encontró ninguna tabla similar a {table_name}")
                    return False
            
            # Obtener estructura de la tabla
            columns_info = self.get_table_structure(table_name)
            if not columns_info:
                logger.error(f"No se pudo obtener la estructura de la tabla {table_name}")
                return False
                
            # Obtener nombres de columnas existentes en la tabla
            table_columns = [col["name"] for col in columns_info]
            
            # Filtrar el DataFrame para incluir solo columnas que existen en la tabla
            df_columns = df.columns.tolist()
            common_columns = list(set(df_columns).intersection(set(table_columns)))
            
            if not common_columns:
                logger.error(f"No hay columnas coincidentes entre el DataFrame y la tabla {table_name}")
                logger.error(f"Columnas del DataFrame: {df_columns}")
                logger.error(f"Columnas de la tabla: {table_columns}")
                return False
                
            # Filtrar DataFrame con las columnas comunes
            filtered_df = df[common_columns]
            
            # Guardar cada fila en la tabla
            for _, row in filtered_df.iterrows():
                # Construir diccionario de valores
                values_dict = {}
                for col in common_columns:
                    values_dict[col] = row[col]
                
                # Construir consulta INSERT
                columns_str = ", ".join([f"[{col}]" for col in values_dict.keys()])
                placeholders = ", ".join(["?" for _ in values_dict.keys()])
                values = list(values_dict.values())
                
                query = f"INSERT INTO [{table_name}] ({columns_str}) VALUES ({placeholders})"
                
                try:
                    self.cursor.execute(query, values)
                except Exception as e:
                    logger.error(f"Error al insertar fila: {str(e)}")
                    logger.error(f"Query: {query}")
                    logger.error(f"Valores: {values}")
                    continue
            
            # Confirmar cambios
            self.conn.commit()
            logger.info(f"Se escribieron {len(filtered_df)} filas en la tabla {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error al escribir en tabla {table_name}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def sync_table(self, db, table_name: str) -> Dict[str, Any]:
        """
        Sincroniza una tabla SQL con su equivalente en MDB
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            table_name: Nombre de la tabla SQL a sincronizar
            
        Returns:
            Dict[str, Any]: Resultado de la sincronización
        """
        result = {
            "success": False,
            "table": table_name,
            "records_count": 0,
            "error": None
        }
        
        try:
            if not self.connected:
                result["error"] = "No hay conexión activa con la base de datos MDB"
                return result
                
            # Verificar si hay un mapeo para esta tabla
            if table_name not in self.table_mappings:
                result["error"] = f"No hay mapeo definido para la tabla {table_name}"
                return result
                
            # Obtener configuración de mapeo
            mapping = self.table_mappings[table_name]
            mdb_table = mapping["mdb_table"]
            column_mapping = mapping["columns"]
            
            # Consultar datos de la tabla SQL
            from sqlalchemy import text
            columns_list = list(column_mapping.keys())
            columns_str = ", ".join(columns_list)
            query = text(f"SELECT {columns_str} FROM {table_name}")
            
            query_result = db.execute(query)
            rows = query_result.fetchall()
            
            if not rows:
                result["success"] = True
                result["message"] = f"No hay datos para sincronizar en la tabla {table_name}"
                return result
                
            # Crear DataFrame con los datos obtenidos
            df = pd.DataFrame(rows, columns=columns_list)
            
            # Renombrar columnas según el mapeo
            df.rename(columns=column_mapping, inplace=True)
            
            # Escribir datos en la tabla MDB
            success = self.write_to_mdb(df, mdb_table)
            
            if success:
                result["success"] = True
                result["records_count"] = len(df)
            else:
                result["error"] = f"Error al escribir datos en la tabla {mdb_table}"
                
            return result
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error al sincronizar tabla {table_name}: {str(e)}")
            logger.error(traceback.format_exc())
            return result

# Instancia global del servicio MDB
mdb_service = MDBService()