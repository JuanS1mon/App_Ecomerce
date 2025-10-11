# Imports de bibliotecas estándar
from Services.app_stock.ot.schema_ot import (
from typing import List, Optional
import logging

# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Imports del proyecto
from db.database import get_db

    OT, OTCreate, OTUpdate,
    Operacion, OperacionCreate, OperacionUpdate,
    ReporteTiempo, ReporteTiempoCreate, ReporteTiempoUpdate
)
# Importar funciones directamente en lugar de clases
from Services.app_stock.ot.service_ot import (
    create_ot, get_ot, gets_ot as get_ots, update_ot, 
    delete_ot, finalizar_ot, verificar_estado_ot
)
from Services.app_stock.articulos.service_operaciones import (
    create_operacion, get_operacion as get_operacion_by_id, gets_operaciones_by_ot as get_operaciones_by_ot,
    update_operacion, delete_operacion, finalizar_operacion,
    create_reporte_tiempo as create_reporte, get_reporte_tiempo as get_reporte_by_id, 
    gets_reportes_tiempo_by_operacion as get_reportes_by_operacion,
    update_reporte_tiempo as update_reporte, delete_reporte_tiempo as delete_reporte
)

# Configuración del logger
logger = logging.getLogger(__name__)

# Router para Órdenes de Trabajo y componentes relacionados
router = APIRouter(
    prefix="/ot",
    tags=["ot"],
    responses={404: {"description": "No encontrado"}},
)

# Rutas para Órdenes de Trabajo (OT)
@router.get("/", response_model=List[OT])
def get_ots(
    skip: int = 0, 
    limit: int = 100, 
    estado: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las órdenes de trabajo con opciones de filtrado
    """
    try:
        if query:
            # TODO: Implementar función de búsqueda
            return get_ots(db)
        elif estado:
            # TODO: Implementar filtro por estado
            return get_ots(db)
        else:
            return get_ots(db)
    except Exception as e:
        logger.error(f"Error al obtener OTs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/id/{ot_id}", response_model=OT)
def get_ot(ot_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una orden de trabajo por su ID
    """
    try:
        db_ot = get_ot(db, ot_id)
        if db_ot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OT con ID {ot_id} no encontrada"
            )
        return db_ot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener OT {ot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/", response_model=OT, status_code=status.HTTP_201_CREATED)
def create_orden_trabajo(ot: OTCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva orden de trabajo
    """
    try:
        return create_ot(db, ot)
    except Exception as e:
        logger.error(f"Error al crear OT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/id/{ot_id}", response_model=OT)
def update_orden_trabajo(ot_id: int, ot: OTUpdate, db: Session = Depends(get_db)):
    """
    Actualiza una orden de trabajo existente
    """
    try:
        db_ot = update_ot(db, ot_id, ot)
        if db_ot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OT con ID {ot_id} no encontrada"
            )
        return db_ot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar OT {ot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/id/{ot_id}")
def delete_orden_trabajo(ot_id: int, db: Session = Depends(get_db)):
    """
    Elimina una orden de trabajo
    """
    try:
        result = delete_ot(db, ot_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OT con ID {ot_id} no encontrada"
            )
        return {"message": f"OT con ID {ot_id} eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar OT {ot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/id/{ot_id}/finalizar")
def finalizar_orden_trabajo(ot_id: int, db: Session = Depends(get_db)):
    """
    Finaliza una orden de trabajo verificando que todas sus operaciones estén finalizadas
    """
    try:
        ot_finalizada = finalizar_ot(db, ot_id)
        return {"message": f"OT con ID {ot_id} finalizada correctamente", "ot": ot_finalizada}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al finalizar OT {ot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

# Rutas para Operaciones
@router.get("/id/{ot_id}/operaciones", response_model=List[Operacion])
def get_operaciones(ot_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todas las operaciones de una OT
    """
    try:
        # Verificar si existe la OT
        db_ot = get_ot(db, ot_id)
        if db_ot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OT con ID {ot_id} no encontrada"
            )
        
        return get_operaciones_by_ot(db, ot_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener operaciones de OT {ot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/operaciones/id/{operacion_id}", response_model=Operacion)
def get_operacion(operacion_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una operación por su ID
    """
    try:
        db_operacion = get_operacion_by_id(db, operacion_id)
        if db_operacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operación con ID {operacion_id} no encontrada"
            )
        return db_operacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener operación {operacion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/operaciones", response_model=Operacion, status_code=status.HTTP_201_CREATED)
def create_operacion(operacion: OperacionCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva operación
    """
    try:
        result = create_operacion(db, operacion)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        return result["operacion"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear operación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/operaciones/id/{operacion_id}", response_model=Operacion)
def update_operacion(operacion_id: int, operacion: OperacionUpdate, db: Session = Depends(get_db)):
    """
    Actualiza una operación existente
    """
    try:
        db_operacion = update_operacion(db, operacion_id, operacion)
        if db_operacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operación con ID {operacion_id} no encontrada"
            )
        return db_operacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar operación {operacion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/operaciones/id/{operacion_id}")
def delete_operacion(operacion_id: int, db: Session = Depends(get_db)):
    """
    Elimina una operación
    """
    try:
        result = delete_operacion(db, operacion_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operación con ID {operacion_id} no encontrada"
            )
        return {"message": f"Operación con ID {operacion_id} eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar operación {operacion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/operaciones/id/{operacion_id}/finalizar")
def finalizar_operacion(operacion_id: int, db: Session = Depends(get_db)):
    """
    Finaliza una operación
    """
    try:
        result = finalizar_operacion(db, operacion_id)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": f"Operación con ID {operacion_id} finalizada correctamente", "operacion": result["operacion"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al finalizar operación {operacion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

# Rutas para Reportes de Tiempo
@router.get("/operaciones/id/{operacion_id}/tiempos", response_model=List[ReporteTiempo])
def get_tiempos(operacion_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los reportes de tiempo de una operación
    """
    try:
        # Verificar si existe la operación
        db_operacion = get_operacion_by_id(db, operacion_id)
        if db_operacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operación con ID {operacion_id} no encontrada"
            )
        
        return get_reportes_by_operacion(db, operacion_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener reportes de tiempo de operación {operacion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/tiempos/id/{tiempo_id}", response_model=ReporteTiempo)
def get_tiempo(tiempo_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un reporte de tiempo por su ID
    """
    try:
        db_tiempo = get_reporte_by_id(db, tiempo_id)
        if db_tiempo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reporte de tiempo con ID {tiempo_id} no encontrado"
            )
        return db_tiempo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener reporte de tiempo {tiempo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/tiempos", response_model=ReporteTiempo, status_code=status.HTTP_201_CREATED)
def create_tiempo(tiempo: ReporteTiempoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo reporte de tiempo
    """
    try:
        result = create_reporte(db, tiempo)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        return result["reporte"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear reporte de tiempo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/tiempos/id/{tiempo_id}", response_model=ReporteTiempo)
def update_tiempo(tiempo_id: int, tiempo: ReporteTiempoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un reporte de tiempo existente
    """
    try:
        db_tiempo = update_reporte(db, tiempo_id, tiempo)
        if db_tiempo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reporte de tiempo con ID {tiempo_id} no encontrado"
            )
        return db_tiempo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar reporte de tiempo {tiempo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/tiempos/id/{tiempo_id}")
def delete_tiempo(tiempo_id: int, db: Session = Depends(get_db)):
    """
    Elimina un reporte de tiempo
    """
    try:
        result = delete_reporte(db, tiempo_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reporte de tiempo con ID {tiempo_id} no encontrado"
            )
        return {"message": f"Reporte de tiempo con ID {tiempo_id} eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar reporte de tiempo {tiempo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )