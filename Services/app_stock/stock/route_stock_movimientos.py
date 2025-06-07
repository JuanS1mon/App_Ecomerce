from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
try:
    from ....db.database import get_db
except ImportError:
    from sql_app.db.database import get_db
# Importamos las funciones de servicio para movimientos de stock
from .stock_movimientos import get_movimientos_pendientes, get_detalle_movimiento, confirmar_movimiento, revertir_confirmacion, cerrar_movimiento, get_historial_confirmaciones
from fastapi.responses import HTMLResponse, FileResponse
import logging
from typing import List, Dict, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ConfirmacionData(BaseModel):
    cantidades: Dict[int, float] = None
    completarMovimiento: bool = False
    observacion: str = None

router = APIRouter(
    prefix="/stock/movimientos",
    tags=["stock_movimientos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pendientes", response_model=List[Dict[str, Any]])
async def routes_get_movimientos_pendientes(
    mostrar_confirmados: bool = False, 
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los movimientos de stock pendientes de confirmación.
    
    Args:
        mostrar_confirmados: Si es True, muestra también los movimientos confirmados
    """
    try:
        movimientos = get_movimientos_pendientes(db, mostrar_confirmados)
        return movimientos
    except Exception as e:
        logger.error(f"Error al obtener movimientos pendientes: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/detalle/{nro_movimiento}/{codigo_art}", response_model=List[Dict[str, Any]])
async def routes_get_detalle_movimiento(
    nro_movimiento: int, 
    codigo_art: int, 
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un movimiento específico por su número y código de artículo.
    """
    try:
        detalle = get_detalle_movimiento(db, nro_movimiento, codigo_art)
        return detalle
    except Exception as e:
        logger.error(f"Error al obtener detalle de movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/confirmar/{nro_movimiento}/{codigo_art}", response_model=Dict[str, Any])
async def routes_confirmar_movimiento(
    nro_movimiento: int, 
    codigo_art: int, 
    datos: ConfirmacionData = None,
    db: Session = Depends(get_db)
):
    """
    Confirma un movimiento de stock, ajustando las cantidades disponibles, reservadas y preparadas.
    
    - Si se proporciona una cantidad específica por depósito, se utilizará esa cantidad para la confirmación.
    - Si no se proporciona ninguna cantidad, se confirmará la cantidad total reservada/preparada.
    """
    try:
        cantidades = datos.cantidades if datos else None
        completar_movimiento = datos.completarMovimiento if datos and hasattr(datos, 'completarMovimiento') else False
        observacion = datos.observacion if datos and hasattr(datos, 'observacion') else None
        
        logger.info(f"Confirmando movimiento {nro_movimiento}/{codigo_art} con cantidades={cantidades}, completar={completar_movimiento}, obs={observacion}")
        
        resultado = confirmar_movimiento(
            db, 
            nro_movimiento, 
            codigo_art, 
            cantidades, 
            completar_movimiento, 
            observacion
        )
        return resultado
    except Exception as e:
        logger.error(f"Error al confirmar movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/revertir-confirmacion/{nro_movimiento}/{codigo_art}", response_model=Dict[str, Any])
async def routes_revertir_confirmacion(
    nro_movimiento: int, 
    codigo_art: int, 
    db: Session = Depends(get_db)
):
    """
    Revierte la confirmación de un movimiento de stock, permitiendo que vuelva a aparecer
    en la lista de movimientos pendientes.
    """
    try:
        resultado = revertir_confirmacion(db, nro_movimiento, codigo_art)
        return resultado
    except Exception as e:
        logger.error(f"Error al revertir confirmación de movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/cerrar/{nro_movimiento}/{codigo_art}", response_model=Dict[str, Any])
async def routes_cerrar_movimiento(
    nro_movimiento: int, 
    codigo_art: int, 
    db: Session = Depends(get_db)
):
    """
    Cierra manualmente un movimiento de stock, incluso si hay cantidades pendientes.
    Esto permite completar un movimiento cuando no es posible confirmar toda la cantidad.
    """
    try:
        resultado = cerrar_movimiento(db, nro_movimiento, codigo_art)
        return resultado
    except Exception as e:
        logger.error(f"Error al cerrar movimiento manualmente: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/historial-confirmaciones/{nro_movimiento}/{codigo_art}", response_model=List[Dict[str, Any]])
async def routes_get_historial_confirmaciones(
    nro_movimiento: int, 
    codigo_art: int, 
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de confirmaciones parciales para un movimiento específico.
    Permite ver cuándo y cómo se fue confirmando un movimiento en varias etapas.
    """
    try:
        historial = get_historial_confirmaciones(db, nro_movimiento, codigo_art)
        return historial
    except Exception as e:
        logger.error(f"Error al obtener historial de confirmaciones: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina_movimientos():
    """
    Devuelve la página HTML para la gestión de movimientos de stock.
    """
    try:
        with open(f"sql_app/static/app_stock/stock/stock_movimientos.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
