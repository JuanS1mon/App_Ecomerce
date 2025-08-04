# Imports de bibliotecas estándar
from sql_app.Services.app_stock.articulos.model_precios_historial import PreciosHistorial
from sql_app.Services.app_stock.articulos.schema_precios_historial import (
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import logging

# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.db.database import get_db

    PreciosHistorialCreate, 
    PreciosHistorialUpdate, 
    PreciosHistorialRead,
    PreciosHistorialFiltro
)
from sql_app.Services.app_stock.articulos.service_precios_historial import (
    registrar_cambio_precio,
    obtener_historial_por_articulo,
    busqueda_avanzada_historial
)

router = APIRouter(
    prefix="/precios-historial",
    tags=["precios"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

logger = logging.getLogger(__name__)

@router.get("/{articulo_id}", response_model=List[PreciosHistorialRead])
async def get_historial_precios(
    articulo_id: int,
    tipo_precio: Optional[str] = Query(None, description="Tipo de precio ('costo' o 'venta')"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (formato YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (formato YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de cambios de precios para un artículo específico
    
    - **articulo_id**: ID del artículo
    - **tipo_precio**: Opcional, filtrar por tipo de precio ('costo' o 'venta')
    - **fecha_desde**: Opcional, fecha desde la cual filtrar
    - **fecha_hasta**: Opcional, fecha hasta la cual filtrar
    """
    try:
        # Convertir dates a datetimes si están presentes
        fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time()) if fecha_desde else None
        fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time()) if fecha_hasta else None
        
        # Validar tipo_precio si se proporciona
        if tipo_precio and tipo_precio not in ['costo', 'venta']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo de precio debe ser 'costo' o 'venta'"
            )
            
        historial = obtener_historial_por_articulo(
            db=db,
            articulo_id=articulo_id,
            tipo_precio=tipo_precio,
            fecha_desde=fecha_desde_dt,
            fecha_hasta=fecha_hasta_dt
        )
        
        return [PreciosHistorialRead.model_validate(item) for item in historial]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de precios: {str(e)}"
        )

@router.get("/", response_model=List[PreciosHistorialRead])
async def buscar_historial_precios(
    articulo_id: Optional[int] = Query(None, description="ID del artículo"),
    tipo_precio: Optional[str] = Query(None, description="Tipo de precio ('costo' o 'venta')"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (formato YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (formato YYYY-MM-DD)"),
    usuario_id: Optional[int] = Query(None, description="ID del usuario que realizó los cambios"),
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(50, description="Elementos por página", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Realiza una búsqueda avanzada en el historial de precios
    
    - **articulo_id**: Opcional, filtrar por artículo
    - **tipo_precio**: Opcional, filtrar por tipo de precio ('costo' o 'venta')
    - **fecha_desde**: Opcional, fecha desde la cual filtrar
    - **fecha_hasta**: Opcional, fecha hasta la cual filtrar
    - **usuario_id**: Opcional, ID del usuario que realizó los cambios
    - **page**: Número de página (mínimo 1)
    - **page_size**: Elementos por página (entre 1 y 100)
    """
    try:
        # Convertir dates a datetimes si están presentes
        fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time()) if fecha_desde else None
        fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time()) if fecha_hasta else None
        
        # Validar tipo_precio si se proporciona
        if tipo_precio and tipo_precio not in ['costo', 'venta']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo de precio debe ser 'costo' o 'venta'"
            )
            
        historial = busqueda_avanzada_historial(
            db=db,
            articulo_id=articulo_id,
            tipo_precio=tipo_precio,
            fecha_desde=fecha_desde_dt,
            fecha_hasta=fecha_hasta_dt,
            usuario_id=usuario_id,
            page=page,
            page_size=page_size
        )
        
        return [PreciosHistorialRead.model_validate(item) for item in historial]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda avanzada de historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda avanzada de historial: {str(e)}"
        )