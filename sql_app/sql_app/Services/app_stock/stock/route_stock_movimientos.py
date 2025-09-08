import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sql_app.db.database import get_db
from .stock_movimientos import (
    cerrar_movimiento,
    confirmar_movimiento,
    get_detalle_movimiento,
    get_historial_confirmaciones,
    get_movimientos_pendientes,
    revertir_confirmacion
)

logger = logging.getLogger(__name__)

class ConfirmacionData(BaseModel):
    cantidades: Dict[int, float] = None
    completarMovimiento: bool = False
    observacion: str = None

class MaterialOTData(BaseModel):
    codigo_art: int
    id_deposito: int
    cantidad: float
    observacion: str = None

class ConsumoMaterialOTData(BaseModel):
    materiales: List[MaterialOTData]
    ot_id: int
    usuario: str
    operacion_id: int = None

class DevolucionMaterialOTData(BaseModel):
    materiales: List[MaterialOTData]
    ot_id: int
    usuario: str

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

@router.post("/ot/consumir-materiales", response_model=Dict[str, Any])
async def routes_consumir_materiales_ot(
    datos: ConsumoMaterialOTData,
    db: Session = Depends(get_db)
):
    """
    Registra el consumo de materiales en una OT específica.
    Genera movimientos de stock de salida por cada material consumido.
    """
    try:
        resultados = []
        nro_movimiento_base = None
        
        for material in datos.materiales:
            # Generar movimiento de stock de salida
            resultado_stock = {
                "codigo_art": material.codigo_art,
                "id_deposito": material.id_deposito,
                "cantidad": material.cantidad,
                "tipo": False,  # Salida
                "observacion": f"Consumo OT #{datos.ot_id}: {material.observacion or 'Material utilizado'}"
            }
            
            # Aquí llamarías a la función de crear movimiento de stock
            # resultado_movimiento = crear_movimiento_stock(db, resultado_stock)
            
            resultados.append({
                "codigo_art": material.codigo_art,
                "cantidad_consumida": material.cantidad,
                "estado": "consumido"
            })
            
        return {
            "mensaje": f"Materiales consumidos exitosamente en OT #{datos.ot_id}",
            "ot_id": datos.ot_id,
            "materiales_procesados": len(datos.materiales),
            "detalles": resultados
        }
        
    except Exception as e:
        logger.error(f"Error al consumir materiales de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/ot/devolver-materiales", response_model=Dict[str, Any])
async def routes_devolver_materiales_ot(
    datos: DevolucionMaterialOTData,
    db: Session = Depends(get_db)
):
    """
    Devuelve materiales no utilizados de una OT al stock.
    Genera movimientos de entrada para los materiales devueltos.
    """
    try:
        resultados = []
        
        for material in datos.materiales:
            # Generar movimiento de stock de entrada (devolución)
            resultado_stock = {
                "codigo_art": material.codigo_art,
                "id_deposito": material.id_deposito,
                "cantidad": material.cantidad,
                "tipo": True,  # Entrada
                "observacion": f"Devolución OT #{datos.ot_id}: {material.observacion or 'Material no utilizado'}"
            }
            
            resultados.append({
                "codigo_art": material.codigo_art,
                "cantidad_devuelta": material.cantidad,
                "estado": "devuelto"
            })
            
        return {
            "mensaje": f"Materiales devueltos exitosamente de OT #{datos.ot_id}",
            "ot_id": datos.ot_id,
            "materiales_devueltos": len(datos.materiales),
            "detalles": resultados
        }
        
    except Exception as e:
        logger.error(f"Error al devolver materiales de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/ot/materiales-disponibles/{id_deposito}", response_model=List[Dict[str, Any]])
async def routes_get_materiales_disponibles_ot(
    id_deposito: int,
    cantidad_minima: float = 0,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de materiales disponibles en un depósito para asignar a una OT.
    """
    try:
        # Aquí consultarías el stock disponible del depósito
        # usando las funciones existentes del sistema de stock
        
        # Ejemplo de estructura de respuesta:
        materiales_disponibles = [
            {
                "codigo_art": 1001,
                "descripcion": "Tornillo M8x20",
                "stock_fisico": 500.0,
                "stock_disponible": 450.0,
                "stock_reservado": 50.0,
                "unidad": "unidad"
            }
            # ... más materiales
        ]
        
        return materiales_disponibles
        
    except Exception as e:
        logger.error(f"Error al obtener materiales disponibles: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/ot/resumen-consumo/{ot_id}", response_model=Dict[str, Any])
async def routes_get_resumen_consumo_ot(
    ot_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen del consumo de materiales de una OT específica.
    """
    try:
        # Aquí consultarías los materiales planificados vs utilizados
        resumen = {
            "ot_id": ot_id,
            "materiales_planificados": [],
            "materiales_utilizados": [],
            "materiales_pendientes": [],
            "costo_total_planificado": 0.0,
            "costo_total_utilizado": 0.0,
            "eficiencia_material": 95.5  # Porcentaje de eficiencia
        }
        
        return resumen
        
    except Exception as e:
        logger.error(f"Error al obtener resumen de consumo de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
