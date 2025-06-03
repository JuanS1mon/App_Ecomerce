from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from .model_precios_historial import PreciosHistorial

logger = logging.getLogger(__name__)

def registrar_cambio_precio(
    db: Session, 
    articulo_id: int,
    precio_anterior: float,
    precio_nuevo: float,
    tipo_precio: str,
    usuario_id: Optional[int] = None,
    motivo: Optional[str] = None
) -> PreciosHistorial:
    """
    Registra un cambio de precio en el historial
    
    Args:
        db: Sesión de base de datos
        articulo_id: ID del artículo
        precio_anterior: Precio anterior
        precio_nuevo: Precio nuevo
        tipo_precio: Tipo de precio ('costo' o 'venta')
        usuario_id: ID del usuario que realiza el cambio
        motivo: Motivo del cambio
    
    Returns:
        Objeto PreciosHistorial creado
    """
    try:
        # Calcular porcentaje de variación
        porcentaje_variacion = None
        if precio_anterior > 0:
            porcentaje_variacion = ((precio_nuevo - precio_anterior) / precio_anterior) * 100
        
        # Crear registro en historial
        historial = PreciosHistorial(
            articulo_id=articulo_id,
            precio_anterior=precio_anterior,
            precio_nuevo=precio_nuevo,
            tipo_precio=tipo_precio,
            usuario_id=usuario_id,
            motivo=motivo,
            porcentaje_variacion=porcentaje_variacion
        )
        
        db.add(historial)
        db.commit()
        db.refresh(historial)
        
        logger.info(f"Cambio de precio registrado: Artículo {articulo_id}, {tipo_precio} - {precio_anterior} -> {precio_nuevo}")
        return historial
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al registrar cambio de precio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar cambio de precio: {str(e)}"
        )

def obtener_historial_por_articulo(
    db: Session,
    articulo_id: int,
    tipo_precio: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> List[PreciosHistorial]:
    """
    Obtiene el historial de cambios de precios para un artículo específico
    
    Args:
        db: Sesión de base de datos
        articulo_id: ID del artículo
        tipo_precio: Filtrar por tipo de precio ('costo' o 'venta')
        fecha_desde: Fecha desde la cual filtrar
        fecha_hasta: Fecha hasta la cual filtrar
    
    Returns:
        Lista de registros de historial de precios
    """
    try:
        query = db.query(PreciosHistorial).filter(PreciosHistorial.articulo_id == articulo_id)
        
        if tipo_precio:
            query = query.filter(PreciosHistorial.tipo_precio == tipo_precio)
            
        if fecha_desde:
            query = query.filter(PreciosHistorial.fecha_cambio >= fecha_desde)
            
        if fecha_hasta:
            query = query.filter(PreciosHistorial.fecha_cambio <= fecha_hasta)
            
        # Ordenar por fecha de cambio (la más reciente primero)
        query = query.order_by(PreciosHistorial.fecha_cambio.desc())
        
        return query.all()
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de precios: {str(e)}"
        )

def busqueda_avanzada_historial(
    db: Session,
    articulo_id: Optional[int] = None,
    tipo_precio: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    usuario_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50
) -> List[PreciosHistorial]:
    """
    Realiza una búsqueda avanzada en el historial de precios
    
    Args:
        db: Sesión de base de datos
        articulo_id: Filtrar por artículo
        tipo_precio: Filtrar por tipo de precio ('costo' o 'venta')
        fecha_desde: Fecha desde la cual filtrar
        fecha_hasta: Fecha hasta la cual filtrar
        usuario_id: Filtrar por usuario que realizó el cambio
        page: Página actual
        page_size: Elementos por página
        
    Returns:
        Lista de registros de historial de precios
    """
    try:
        query = db.query(PreciosHistorial)
        
        # Aplicar filtros si se proporcionan
        if articulo_id:
            query = query.filter(PreciosHistorial.articulo_id == articulo_id)
            
        if tipo_precio:
            query = query.filter(PreciosHistorial.tipo_precio == tipo_precio)
            
        if fecha_desde:
            query = query.filter(PreciosHistorial.fecha_cambio >= fecha_desde)
            
        if fecha_hasta:
            query = query.filter(PreciosHistorial.fecha_cambio <= fecha_hasta)
            
        if usuario_id:
            query = query.filter(PreciosHistorial.usuario_id == usuario_id)
            
        # Ordenar por fecha (la más reciente primero)
        query = query.order_by(PreciosHistorial.fecha_cambio.desc())
        
        # Aplicar paginación
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        return query.all()
    
    except SQLAlchemyError as e:
        logger.error(f"Error en búsqueda avanzada de historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda avanzada de historial: {str(e)}"
        )