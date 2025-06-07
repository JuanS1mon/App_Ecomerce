from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text, func, and_, or_
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from .model_calidad import CalidadBloqueo

logger = logging.getLogger(__name__)

def bloquear_stock_por_calidad(
    db: Session, 
    id_deposito: int, 
    codigo_art: int, 
    cantidad: float,
    motivo: str,
    usuario: Optional[str] = None,
    observaciones: Optional[str] = None
) -> Dict[str, Any]:
    """
    Bloquea una cantidad de stock por motivos de calidad.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        cantidad: Cantidad a bloquear
        motivo: Motivo del bloqueo
        usuario: Usuario que realiza el bloqueo
        observaciones: Observaciones adicionales
        
    Returns:
        Diccionario con información del bloqueo creado
    """
    try:
        if cantidad <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad a bloquear debe ser mayor que cero"
            )
            
        # Crear registro de bloqueo
        bloqueo = CalidadBloqueo(
            id_deposito=id_deposito,
            codigo_art=codigo_art,
            cantidad=cantidad,
            motivo=motivo,
            fecha_bloqueo=datetime.now(),
            usuario_bloqueo=usuario,
            observaciones=observaciones,
            activo=True
        )
        
        db.add(bloqueo)
        db.commit()
        db.refresh(bloqueo)
        
        logger.info(f"Stock bloqueado por calidad: depósito={id_deposito}, artículo={codigo_art}, cantidad={cantidad}")
        
        return {
            "id_bloqueo": bloqueo.id,
            "id_deposito": bloqueo.id_deposito,
            "codigo_art": bloqueo.codigo_art,
            "cantidad": bloqueo.cantidad,
            "motivo": bloqueo.motivo,
            "fecha_bloqueo": bloqueo.fecha_bloqueo,
            "usuario_bloqueo": bloqueo.usuario_bloqueo,
            "observaciones": bloqueo.observaciones
        }
        
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al bloquear stock por calidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al bloquear stock por calidad: {str(e)}"
        )

def liberar_stock_bloqueado(
    db: Session, 
    id_bloqueo: int,
    usuario: Optional[str] = None,
    observaciones: Optional[str] = None
) -> Dict[str, Any]:
    """
    Libera un bloqueo de stock por calidad.
    
    Args:
        db: Sesión de base de datos
        id_bloqueo: ID del bloqueo a liberar
        usuario: Usuario que realiza la liberación
        observaciones: Observaciones adicionales sobre la liberación
        
    Returns:
        Diccionario con información del bloqueo liberado
    """
    try:
        # Buscar el bloqueo
        bloqueo = db.query(CalidadBloqueo).filter(CalidadBloqueo.id == id_bloqueo).first()
        
        if not bloqueo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró bloqueo con ID {id_bloqueo}"
            )
            
        if not bloqueo.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El bloqueo con ID {id_bloqueo} ya fue liberado"
            )
            
        # Actualizar el bloqueo
        bloqueo.activo = False
        bloqueo.fecha_liberacion = datetime.now()
        bloqueo.usuario_liberacion = usuario
        
        # Añadir observaciones de liberación a las existentes
        if observaciones:
            if bloqueo.observaciones:
                bloqueo.observaciones += f"\n\nLIBERACIÓN [{datetime.now().strftime('%Y-%m-%d %H:%M')}]: {observaciones}"
            else:
                bloqueo.observaciones = f"LIBERACIÓN [{datetime.now().strftime('%Y-%m-%d %H:%M')}]: {observaciones}"
        
        db.commit()
        db.refresh(bloqueo)
        
        logger.info(f"Stock liberado de bloqueo por calidad: bloqueo={id_bloqueo}, depósito={bloqueo.id_deposito}, "
                   f"artículo={bloqueo.codigo_art}, cantidad={bloqueo.cantidad}")
        
        return {
            "id_bloqueo": bloqueo.id,
            "id_deposito": bloqueo.id_deposito,
            "codigo_art": bloqueo.codigo_art,
            "cantidad": bloqueo.cantidad,
            "motivo": bloqueo.motivo,
            "fecha_bloqueo": bloqueo.fecha_bloqueo,
            "fecha_liberacion": bloqueo.fecha_liberacion,
            "usuario_bloqueo": bloqueo.usuario_bloqueo,
            "usuario_liberacion": bloqueo.usuario_liberacion,
            "observaciones": bloqueo.observaciones
        }
        
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al liberar stock bloqueado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al liberar stock bloqueado: {str(e)}"
        )

def listar_bloqueos_calidad(
    db: Session, 
    id_deposito: Optional[int] = None, 
    codigo_art: Optional[int] = None,
    solo_activos: bool = True
) -> List[Dict[str, Any]]:
    """
    Lista los bloqueos de stock por calidad, con opción de filtrar por depósito y/o artículo.
    
    Args:
        db: Sesión de base de datos
        id_deposito: Filtro opcional por ID de depósito
        codigo_art: Filtro opcional por código de artículo
        solo_activos: Si es True, solo muestra bloqueos activos
        
    Returns:
        Lista de diccionarios con información de los bloqueos
    """
    try:
        # Crear la consulta base
        query = db.query(CalidadBloqueo)
        
        # Aplicar filtros si se proporcionan
        if id_deposito is not None:
            query = query.filter(CalidadBloqueo.id_deposito == id_deposito)
            
        if codigo_art is not None:
            query = query.filter(CalidadBloqueo.codigo_art == codigo_art)
            
        if solo_activos:
            query = query.filter(CalidadBloqueo.activo == True)
            
        # Ordenar por fecha de bloqueo (más recientes primero)
        bloqueos = query.order_by(CalidadBloqueo.fecha_bloqueo.desc()).all()
        
        # Convertir a lista de diccionarios
        result = []
        for bloqueo in bloqueos:
            result.append({
                "id_bloqueo": bloqueo.id,
                "id_deposito": bloqueo.id_deposito,
                "codigo_art": bloqueo.codigo_art,
                "cantidad": bloqueo.cantidad,
                "motivo": bloqueo.motivo,
                "fecha_bloqueo": bloqueo.fecha_bloqueo,
                "fecha_liberacion": bloqueo.fecha_liberacion,
                "usuario_bloqueo": bloqueo.usuario_bloqueo,
                "usuario_liberacion": bloqueo.usuario_liberacion,
                "activo": bloqueo.activo,
                "observaciones": bloqueo.observaciones
            })
            
        return result
        
    except SQLAlchemyError as e:
        logger.error(f"Error al listar bloqueos de calidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar bloqueos de calidad: {str(e)}"
        )
