
# Imports de bibliotecas estándar
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.Services.app_stock.articulos.model_articulos import Articulos
from sql_app.Services.app_stock.articulos.model_precios_historial import PreciosHistorial
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def get_historial_precios_con_filtros(
    db: Session,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    tipo_precio: Optional[str] = None,
    filtro_articulo: Optional[str] = None,
    tipo_variacion: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Obtiene el historial de precios con filtros aplicados.
    
    Args:
        db: Sesión de base de datos
        fecha_desde: Fecha de inicio para el filtro
        fecha_hasta: Fecha de fin para el filtro
        tipo_precio: Tipo de precio ('costo', 'venta', 'todos')
        filtro_articulo: Filtro por código o descripción de artículo
        tipo_variacion: Tipo de variación ('aumento', 'disminucion', 'todos')
        limit: Límite de resultados
        offset: Offset para paginación
        
    Returns:
        Diccionario con historial y estadísticas
    """
    try:
        # Query base con JOIN a la tabla de artículos
        query = db.query(PreciosHistorial).join(Articulos, PreciosHistorial.articulo_id == Articulos.id)
        
        # Aplicar filtros
        if fecha_desde:
            query = query.filter(PreciosHistorial.fecha_cambio >= fecha_desde)
            
        if fecha_hasta:
            query = query.filter(PreciosHistorial.fecha_cambio <= fecha_hasta)
            
        if tipo_precio and tipo_precio != "todos":
            query = query.filter(PreciosHistorial.tipo_precio == tipo_precio)
            
        if filtro_articulo:
            filtro_articulo = f"%{filtro_articulo}%"
            query = query.filter(
                or_(
                    Articulos.codigo.ilike(filtro_articulo),
                    Articulos.descripcion.ilike(filtro_articulo)
                )
            )
            
        if tipo_variacion and tipo_variacion != "todos":
            if tipo_variacion == "aumento":
                query = query.filter(PreciosHistorial.precio_nuevo > PreciosHistorial.precio_anterior)
            elif tipo_variacion == "disminucion":
                query = query.filter(PreciosHistorial.precio_nuevo < PreciosHistorial.precio_anterior)
        
        # Ordenar por fecha descendente
        query = query.order_by(desc(PreciosHistorial.fecha_cambio))
        
        # Obtener total de registros
        total = query.count()
        
        # Aplicar paginación
        historial_items = query.offset(offset).limit(limit).all()
        
        # Convertir a formato de respuesta
        historial = []
        for item in historial_items:
            articulo = item.articulo  # Acceder al artículo relacionado
            historial.append({
                "id": item.id,
                "articulo_id": item.articulo_id,
                "codigo": articulo.codigo if articulo else "N/A",
                "descripcion": articulo.descripcion if articulo else "N/A",
                "precio_anterior": float(item.precio_anterior),
                "precio_nuevo": float(item.precio_nuevo),
                "tipo_precio": item.tipo_precio,
                "fecha_cambio": item.fecha_cambio.isoformat() if item.fecha_cambio else None,
                "usuario_id": item.usuario_id,
                "motivo": item.motivo,
                "variacion_porcentual": round(
                    ((item.precio_nuevo - item.precio_anterior) / item.precio_anterior * 100) 
                    if item.precio_anterior > 0 else 0, 2
                ),
                "variacion_absoluta": round(item.precio_nuevo - item.precio_anterior, 2)
            })
            
        return {
            "historial": historial,
            "total": total,
            "offset": offset,
            "limit": limit,
            "filtros_aplicados": {
                "fecha_desde": fecha_desde.isoformat() if fecha_desde else None,
                "fecha_hasta": fecha_hasta.isoformat() if fecha_hasta else None,
                "tipo_precio": tipo_precio,
                "filtro_articulo": filtro_articulo,
                "tipo_variacion": tipo_variacion
            }
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener historial de precios"
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

def get_estadisticas_historial_precios(
    db: Session,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Obtiene estadísticas del historial de precios.
    
    Args:
        db: Sesión de base de datos
        fecha_desde: Fecha de inicio para el filtro
        fecha_hasta: Fecha de fin para el filtro
        
    Returns:
        Diccionario con estadísticas
    """
    try:
        query = db.query(PreciosHistorial)
        
        # Aplicar filtros de fecha
        if fecha_desde:
            query = query.filter(PreciosHistorial.fecha_cambio >= fecha_desde)
        if fecha_hasta:
            query = query.filter(PreciosHistorial.fecha_cambio <= fecha_hasta)
            
        # Estadísticas generales
        total_cambios = query.count()
        cambios_costo = query.filter(PreciosHistorial.tipo_precio == "costo").count()
        cambios_venta = query.filter(PreciosHistorial.tipo_precio == "venta").count()
        
        # Cambios con aumento vs disminución
        aumentos = query.filter(PreciosHistorial.precio_nuevo > PreciosHistorial.precio_anterior).count()
        disminuciones = query.filter(PreciosHistorial.precio_nuevo < PreciosHistorial.precio_anterior).count()
        
        # Variación promedio
        variaciones = []
        for item in query.all():
            if item.precio_anterior > 0:
                variacion = ((item.precio_nuevo - item.precio_anterior) / item.precio_anterior) * 100
                variaciones.append(variacion)
        
        variacion_promedio = sum(variaciones) / len(variaciones) if variaciones else 0
        
        return {
            "total_cambios": total_cambios,
            "cambios_por_tipo": {
                "costo": cambios_costo,
                "venta": cambios_venta
            },
            "tendencia": {
                "aumentos": aumentos,
                "disminuciones": disminuciones
            },
            "variacion_promedio_porcentual": round(variacion_promedio, 2),
            "periodo": {
                "fecha_desde": fecha_desde.isoformat() if fecha_desde else None,
                "fecha_hasta": fecha_hasta.isoformat() if fecha_hasta else None
            }
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

def get_historial_precios_por_articulo(
    db: Session,
    articulo_id: int,
    tipo_precio: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de precios para un artículo específico.
    
    Args:
        db: Sesión de base de datos
        articulo_id: ID del artículo
        tipo_precio: Tipo de precio ('costo', 'venta')
        fecha_desde: Fecha de inicio para el filtro
        fecha_hasta: Fecha de fin para el filtro
        limit: Límite de resultados
        
    Returns:
        Lista de cambios de precio para el artículo
    """
    try:
        query = db.query(PreciosHistorial).filter(PreciosHistorial.articulo_id == articulo_id)
        
        # Aplicar filtros
        if tipo_precio:
            query = query.filter(PreciosHistorial.tipo_precio == tipo_precio)
            
        if fecha_desde:
            query = query.filter(PreciosHistorial.fecha_cambio >= fecha_desde)
            
        if fecha_hasta:
            query = query.filter(PreciosHistorial.fecha_cambio <= fecha_hasta)
            
        # Ordenar por fecha descendente
        query = query.order_by(desc(PreciosHistorial.fecha_cambio))
        
        # Aplicar límite
        historial_items = query.limit(limit).all()
        
        # Convertir a formato de respuesta
        historial = []
        for item in historial_items:
            historial.append({
                "id": item.id,
                "precio_anterior": float(item.precio_anterior),
                "precio_nuevo": float(item.precio_nuevo),
                "tipo_precio": item.tipo_precio,
                "fecha_cambio": item.fecha_cambio.isoformat() if item.fecha_cambio else None,
                "usuario_id": item.usuario_id,
                "motivo": item.motivo,
                "variacion_porcentual": round(
                    ((item.precio_nuevo - item.precio_anterior) / item.precio_anterior * 100) 
                    if item.precio_anterior > 0 else 0, 2
                ),
                "variacion_absoluta": round(item.precio_nuevo - item.precio_anterior, 2)
            })
            
        return historial
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener historial por artículo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener historial del artículo"
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener historial por artículo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
