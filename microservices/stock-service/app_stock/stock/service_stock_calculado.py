# Imports de bibliotecas estándar
from typing import Any, Dict, List
import logging

# Imports de terceros
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def get_depositos_con_stock(db: Session) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de depósitos que tienen stock.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Lista de depósitos con stock
    """
    try:
        depositos_result = db.execute(text("""
            SELECT DISTINCT d.id, d.descripcion
            FROM depositos d
            INNER JOIN stock s ON d.id = s.id_deposito
            ORDER BY d.id
        """)).fetchall()
        
        return [
            {
                "id": dep.id,
                "descripcion": dep.descripcion or f"Depósito {dep.id}"
            }
            for dep in depositos_result
        ]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener depósitos con stock: {e}")
        # Devolver depósitos de ejemplo en caso de error
        return [
            {"id": 1, "descripcion": "Depósito Principal"},
            {"id": 2, "descripcion": "Depósito Secundario"},
            {"id": 3, "descripcion": "Depósito Auxiliar"}
        ]

def get_depositos_disponibles(db: Session) -> List[Dict[str, Any]]:
    """
    Obtiene todos los depósitos disponibles para consultas de stock.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Lista de todos los depósitos
    """
    try:
        depositos_result = db.execute(text("""
            SELECT d.id, d.descripcion
            FROM depositos d
            ORDER BY d.id
        """)).fetchall()
        
        return [
            {
                "id": dep.id,
                "descripcion": dep.descripcion or f"Depósito {dep.id}"
            }
            for dep in depositos_result
        ]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener depósitos disponibles: {e}")
        # Devolver depósitos de ejemplo en caso de error
        return [
            {"id": 1, "descripcion": "Depósito Principal"},
            {"id": 2, "descripcion": "Depósito Secundario"},
            {"id": 3, "descripcion": "Depósito Auxiliar"}
        ]

def get_articulo_info(db: Session, codigo_art: int) -> Dict[str, Any]:
    """
    Obtiene información de un artículo por su código.
    
    Args:
        db: Sesión de base de datos
        codigo_art: Código del artículo
        
    Returns:
        Información del artículo
    """
    try:
        articulo = db.execute(text("""
            SELECT a.descripcion 
            FROM articulos a 
            WHERE a.id = :codigo_art
        """), {"codigo_art": codigo_art}).fetchone()
        
        return {
            "codigo_art": codigo_art,
            "descripcion": articulo[0] if articulo else "Desconocido"
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener información del artículo {codigo_art}: {e}")
        return {
            "codigo_art": codigo_art,
            "descripcion": "Desconocido"
        }

def get_deposito_info(db: Session, id_deposito: int) -> Dict[str, Any]:
    """
    Obtiene información de un depósito por su ID.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        
    Returns:
        Información del depósito
    """
    try:
        deposito = db.execute(text("""
            SELECT d.descripcion 
            FROM depositos d 
            WHERE d.id = :id_deposito
        """), {"id_deposito": id_deposito}).fetchone()
        
        return {
            "id": id_deposito,
            "descripcion": deposito[0] if deposito else f"Depósito {id_deposito}"
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener información del depósito {id_deposito}: {e}")
        return {
            "id": id_deposito,
            "descripcion": f"Depósito {id_deposito}"
        }

def get_articulos_en_deposito(db: Session, id_deposito: int) -> List[int]:
    """
    Obtiene la lista de códigos de artículos únicos en un depósito.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        
    Returns:
        Lista de códigos de artículos
    """
    try:
        from Services.app_stock.stock.model_stock import Stock as StockModel
        
        articulos = db.query(StockModel.codigo_art).filter(
            StockModel.id_deposito == id_deposito
        ).distinct().all()
        
        return [art[0] for art in articulos]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artículos del depósito {id_deposito}: {e}")
        return []

def get_depositos_con_articulo(db: Session, codigo_art: int) -> List[int]:
    """
    Obtiene la lista de depósitos que contienen un artículo específico.
    
    Args:
        db: Sesión de base de datos
        codigo_art: Código del artículo
        
    Returns:
        Lista de IDs de depósitos
    """
    try:
        from Services.app_stock.stock.model_stock import Stock as StockModel
        
        depositos = db.query(StockModel.id_deposito).filter(
            StockModel.codigo_art == codigo_art
        ).distinct().all()
        
        return [dep[0] for dep in depositos]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener depósitos con artículo {codigo_art}: {e}")
        return []

def get_ultimo_registro_stock(db: Session, id_deposito: int, codigo_art: int) -> Dict[str, Any]:
    """
    Obtiene el último registro de stock almacenado para un artículo en un depósito.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        
    Returns:
        Información del último registro de stock
    """
    try:
        from Services.app_stock.stock.model_stock import Stock as StockModel
        from sqlalchemy import and_
        
        ultimo_registro = db.query(StockModel).filter(
            and_(
                StockModel.id_deposito == id_deposito,
                StockModel.codigo_art == codigo_art
            )
        ).order_by(StockModel.id.desc()).first()
        
        if ultimo_registro:
            return {
                "fisico": float(ultimo_registro.cant_disponible),
                "reservado": float(ultimo_registro.cant_reservado),
                "preparado": float(ultimo_registro.cant_preparado),
                "bloqueado": 0.0  # No tenemos este concepto almacenado aún
            }
        else:
            return {
                "fisico": 0.0,
                "reservado": 0.0,
                "preparado": 0.0,
                "bloqueado": 0.0
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener último registro de stock para depósito {id_deposito}, artículo {codigo_art}: {e}")
        return {
            "fisico": 0.0,
            "reservado": 0.0,
            "preparado": 0.0,
            "bloqueado": 0.0
        }

def validar_existencia_articulo(db: Session, codigo_art: int) -> bool:
    """
    Valida si un artículo existe en la base de datos.
    
    Args:
        db: Sesión de base de datos
        codigo_art: Código del artículo
        
    Returns:
        True si el artículo existe, False en caso contrario
    """
    try:
        result = db.execute(text("""
            SELECT COUNT(*) as count
            FROM articulos a 
            WHERE a.id = :codigo_art
        """), {"codigo_art": codigo_art}).fetchone()
        
        return result.count > 0 if result else False
    except SQLAlchemyError as e:
        logger.error(f"Error al validar existencia del artículo {codigo_art}: {e}")
        return False

def validar_existencia_deposito(db: Session, id_deposito: int) -> bool:
    """
    Valida si un depósito existe en la base de datos.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        
    Returns:
        True si el depósito existe, False en caso contrario
    """
    try:
        result = db.execute(text("""
            SELECT COUNT(*) as count
            FROM depositos d 
            WHERE d.id = :id_deposito
        """), {"id_deposito": id_deposito}).fetchone()
        
        return result.count > 0 if result else False
    except SQLAlchemyError as e:
        logger.error(f"Error al validar existencia del depósito {id_deposito}: {e}")
        return False

def get_articulos_info_batch(db: Session, codigos_art: List[int]) -> Dict[int, str]:
    """
    Obtiene información de múltiples artículos en una sola consulta.
    
    Args:
        db: Sesión de base de datos
        codigos_art: Lista de códigos de artículos
        
    Returns:
        Diccionario con código del artículo como clave y descripción como valor
    """
    try:
        if not codigos_art:
            return {}
            
        # Convertir lista a string para usar en la consulta SQL
        codigos_str = ",".join(map(str, codigos_art))
        
        articulos = db.execute(text(f"""
            SELECT a.id, a.descripcion 
            FROM articulos a 
            WHERE a.id IN ({codigos_str})
        """)).fetchall()
        
        return {
            art.id: art.descripcion or f"Artículo {art.id}"
            for art in articulos
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener información de artículos en lote: {e}")
        return {codigo: f"Artículo {codigo}" for codigo in codigos_art}

def get_depositos_info_batch(db: Session, ids_deposito: List[int]) -> Dict[int, str]:
    """
    Obtiene información de múltiples depósitos en una sola consulta.
    
    Args:
        db: Sesión de base de datos
        ids_deposito: Lista de IDs de depósitos
        
    Returns:
        Diccionario con ID del depósito como clave y descripción como valor
    """
    try:
        if not ids_deposito:
            return {}
            
        # Convertir lista a string para usar en la consulta SQL
        ids_str = ",".join(map(str, ids_deposito))
        
        depositos = db.execute(text(f"""
            SELECT d.id, d.descripcion 
            FROM depositos d 
            WHERE d.id IN ({ids_str})
        """)).fetchall()
        
        return {
            dep.id: dep.descripcion or f"Depósito {dep.id}"
            for dep in depositos
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener información de depósitos en lote: {e}")
        return {id_dep: f"Depósito {id_dep}" for id_dep in ids_deposito}

def get_depositos_con_stock_activo(db: Session) -> List[Dict[str, Any]]:
    """
    Obtiene lista de depósitos que tienen movimientos de stock.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Lista de diccionarios con información de depósitos
    """
    try:
        depositos = db.execute(text("""
            SELECT DISTINCT d.id, d.descripcion
            FROM depositos d
            INNER JOIN stock s ON d.id = s.id_deposito
            ORDER BY d.id
        """)).fetchall()
        
        return [
            {
                "id": dep.id,
                "descripcion": dep.descripcion or f"Depósito {dep.id}"
            }
            for dep in depositos
        ]
    except Exception as e:
        logger.error(f"Error al obtener depósitos con stock: {e}")
        # Devolver depósitos de ejemplo en caso de error
        return [
            {"id": 1, "descripcion": "Depósito Principal"},
            {"id": 2, "descripcion": "Depósito Secundario"},
            {"id": 3, "descripcion": "Depósito Auxiliar"}
        ]

def get_articulos_distintos_en_deposito(db: Session, id_deposito: int) -> List[int]:
    """
    Obtiene todos los códigos de artículos distintos en un depósito específico.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        
    Returns:
        Lista de códigos de artículos
    """
    try:
        from Services.app_stock.stock.model_stock import Stock as StockModel
        
        articulos = db.query(StockModel.codigo_art).filter(
            StockModel.id_deposito == id_deposito
        ).distinct().all()
        
        return [art[0] for art in articulos]
    except Exception as e:
        logger.error(f"Error al obtener artículos en depósito {id_deposito}: {e}")
        return []

def get_depositos_distintos_con_articulo(db: Session, codigo_art: int) -> List[int]:
    """
    Obtiene todos los IDs de depósitos que tienen un artículo específico.
    
    Args:
        db: Sesión de base de datos
        codigo_art: Código del artículo
        
    Returns:
        Lista de IDs de depósitos
    """
    try:
        from Services.app_stock.stock.model_stock import Stock as StockModel
        
        depositos = db.query(StockModel.id_deposito).filter(
            StockModel.codigo_art == codigo_art
        ).distinct().all()
        
        return [dep[0] for dep in depositos]
    except Exception as e:
        logger.error(f"Error al obtener depósitos con artículo {codigo_art}: {e}")
        return []

def get_ultimo_stock_almacenado(db: Session, id_deposito: int, codigo_art: int) -> Dict[str, float]:
    """
    Obtiene el último registro de stock almacenado para un artículo en un depósito.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        
    Returns:
        Diccionario con las cantidades del último registro
    """
    try:
        from Services.app_stock.stock.model_stock import Stock as StockModel
        from sqlalchemy import and_
        
        ultimo_registro = db.query(StockModel).filter(
            and_(
                StockModel.id_deposito == id_deposito,
                StockModel.codigo_art == codigo_art
            )
        ).order_by(StockModel.id.desc()).first()
        
        if ultimo_registro:
            return {
                "fisico": float(ultimo_registro.cant_disponible),
                "reservado": float(ultimo_registro.cant_reservado), 
                "preparado": float(ultimo_registro.cant_preparado),
                "bloqueado": 0.0  # No tenemos este concepto almacenado aún
            }
        else:
            return {
                "fisico": 0.0,
                "reservado": 0.0,
                "preparado": 0.0,
                "bloqueado": 0.0
            }
    except Exception as e:
        logger.error(f"Error al obtener último stock almacenado: {e}")
        return {
            "fisico": 0.0,
            "reservado": 0.0,
            "preparado": 0.0,
            "bloqueado": 0.0
        }

def get_articulos_con_stock_positivo(db: Session, limite: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Obtiene artículos que tienen stock positivo de manera optimizada.
    
    Args:
        db: Sesión de base de datos
        limite: Límite de registros para paginación
        offset: Desplazamiento para paginación
        
    Returns:
        Lista de artículos con stock positivo
    """
    try:
        # Cambiado a LEFT JOIN para manejar casos donde no existen registros en articulos/depositos
        query = text("""
            SELECT 
                s.codigo_art,
                s.id_deposito,
                ISNULL(a.descripcion, 'Artículo ' + CAST(s.codigo_art AS VARCHAR)) as articulo_descripcion,
                ISNULL(d.descripcion, 'Depósito ' + CAST(s.id_deposito AS VARCHAR)) as deposito_descripcion,
                SUM(s.cant_disponible) as stock_fisico,
                SUM(s.cant_reservado) as stock_reservado,
                SUM(s.cant_preparado) as stock_preparado
            FROM stock s
            LEFT JOIN articulos a ON s.codigo_art = a.id
            LEFT JOIN depositos d ON s.id_deposito = d.id
            WHERE s.cant_disponible > 0
            GROUP BY s.codigo_art, s.id_deposito, a.descripcion, d.descripcion
            ORDER BY SUM(s.cant_disponible) DESC, s.codigo_art, s.id_deposito
            OFFSET :offset ROWS FETCH NEXT :limite ROWS ONLY
        """)
        
        result = db.execute(query, {'offset': offset, 'limite': limite}).fetchall()
        print("Resultados SQL obtenidos:", result)  # Agregar print para depuración
        if not result:
            logger.warning("La consulta no devolvió resultados.")
            return []

        try:
            # Convertir cada fila en un diccionario usando los nombres de las columnas
            return [
                {
                    "codigo_art": row[0],
                    "id_deposito": row[1],
                    "articulo_descripcion": row[2],
                    "deposito_descripcion": row[3],
                    "stock_fisico": row[4],
                    "stock_reservado": row[5],
                    "stock_preparado": row[6]
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error al convertir resultados en diccionarios: {e}")
            return []
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artículos con stock positivo: {e}")
        return []

def contar_articulos_con_stock_positivo(db: Session) -> int:
    """
    Cuenta el total de artículos con stock positivo para paginación.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Número total de artículos con stock positivo
    """
    try:
        query = text("""
            SELECT COUNT(*)
            FROM (
                SELECT s.codigo_art, s.id_deposito
                FROM stock s
                WHERE s.cant_disponible > 0
                GROUP BY s.codigo_art, s.id_deposito
            ) subquery
        """)
        
        result = db.execute(query).scalar()
        return result or 0
    except SQLAlchemyError as e:
        logger.error(f"Error al contar artículos con stock positivo: {e}")
        return 0

def get_resumen_stock_global(db: Session) -> Dict[str, Any]:
    """
    Obtiene un resumen del stock global para vista ejecutiva.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Resumen del stock global
    """
    try:
        query = text("""
            SELECT 
                COUNT(DISTINCT s.codigo_art) as total_articulos,
                COUNT(DISTINCT s.id_deposito) as total_depositos,
                COUNT(DISTINCT CAST(s.codigo_art AS VARCHAR) + '-' + CAST(s.id_deposito AS VARCHAR)) as total_ubicaciones,
                COUNT(CASE WHEN s.cant_disponible > 0 THEN 1 END) as ubicaciones_con_stock,
                SUM(s.cant_disponible) as stock_total,
                SUM(s.cant_reservado) as reservado_total,
                SUM(s.cant_preparado) as preparado_total,
                AVG(s.cant_disponible) as stock_promedio,
                MAX(s.cant_disponible) as stock_maximo,
                MIN(CASE WHEN s.cant_disponible > 0 THEN s.cant_disponible END) as stock_minimo_positivo
            FROM stock s
        """)
        
        result = db.execute(query).fetchone()
        
        if result:
            return {
                "total_articulos": result.total_articulos or 0,
                "total_depositos": result.total_depositos or 0,
                "total_ubicaciones": result.total_ubicaciones or 0,
                "ubicaciones_con_stock": result.ubicaciones_con_stock or 0,
                "stock_total": float(result.stock_total) if result.stock_total else 0.0,
                "reservado_total": float(result.reservado_total) if result.reservado_total else 0.0,
                "preparado_total": float(result.preparado_total) if result.preparado_total else 0.0,
                "stock_promedio": float(result.stock_promedio) if result.stock_promedio else 0.0,
                "stock_maximo": float(result.stock_maximo) if result.stock_maximo else 0.0,
                "stock_minimo_positivo": float(result.stock_minimo_positivo) if result.stock_minimo_positivo else 0.0,
                "porcentaje_ocupacion": round((result.ubicaciones_con_stock / result.total_ubicaciones * 100), 2) if result.total_ubicaciones > 0 else 0.0
            }
        else:
            return {
                "total_articulos": 0,
                "total_depositos": 0,
                "total_ubicaciones": 0,
                "ubicaciones_con_stock": 0,
                "stock_total": 0.0,
                "reservado_total": 0.0,
                "preparado_total": 0.0,
                "stock_promedio": 0.0,
                "stock_maximo": 0.0,
                "stock_minimo_positivo": 0.0,
                "porcentaje_ocupacion": 0.0
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener resumen de stock global: {e}")
        return {
            "total_articulos": 0,
            "total_depositos": 0,
            "total_ubicaciones": 0,
            "ubicaciones_con_stock": 0,
            "stock_total": 0.0,
            "reservado_total": 0.0,
            "preparado_total": 0.0,
            "stock_promedio": 0.0,
            "stock_maximo": 0.0,
            "stock_minimo_positivo": 0.0,
            "porcentaje_ocupacion": 0.0
        }

def get_top_articulos_por_stock(db: Session, limite: int = 50) -> List[Dict[str, Any]]:
    """
    Obtiene los artículos con mayor stock de manera consolidada.
    
    Args:
        db: Sesión de base de datos
        limite: Número de artículos a retornar
        
    Returns:
        Lista de artículos con mayor stock consolidado
    """
    try:
        query = text("""
            SELECT TOP (:limite)
                s.codigo_art,
                COALESCE(a.descripcion, 'Artículo ' + CAST(s.codigo_art AS VARCHAR)) as articulo_descripcion,
                SUM(s.cant_disponible) as stock_total,
                SUM(s.cant_reservado) as reservado_total,
                SUM(s.cant_preparado) as preparado_total,
                COUNT(DISTINCT s.id_deposito) as depositos_con_stock,
                AVG(s.cant_disponible) as stock_promedio_por_deposito
            FROM stock s
            LEFT JOIN articulos a ON s.codigo_art = a.id
            WHERE s.cant_disponible > 0
            GROUP BY s.codigo_art, a.descripcion
            ORDER BY SUM(s.cant_disponible) DESC
        """)
        
        result = db.execute(query, {"limite": limite}).fetchall()
        
        return [
            {
                "codigo_art": row.codigo_art,
                "articulo_descripcion": row.articulo_descripcion or f"Artículo {row.codigo_art}",
                "stock_total": float(row.stock_total) if row.stock_total else 0.0,
                "reservado_total": float(row.reservado_total) if row.reservado_total else 0.0,
                "preparado_total": float(row.preparado_total) if row.preparado_total else 0.0,
                "depositos_con_stock": row.depositos_con_stock or 0,
                "stock_promedio_por_deposito": float(row.stock_promedio_por_deposito) if row.stock_promedio_por_deposito else 0.0,
                "disponible_total": float(row.stock_total or 0) - float(row.reservado_total or 0) - float(row.preparado_total or 0)
            }
            for row in result
        ]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener top artículos por stock: {e}")
        return []