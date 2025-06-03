from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_ot import OTCreate as OtCreate, OTUpdate as OtUpdate, OT as OtRead, OperacionCreate, OperacionUpdate, Operacion as OperacionRead, ReporteTiempoCreate, ReporteTiempoUpdate, ReporteTiempo as ReporteTiempoRead
from .model_ot import OT as OtModel, Operacion as OperacionModel, ReporteTiempo as ReporteTiempoModel
from .service_ot import create_ot, get_ot, gets_ot, delete_ot, update_ot, finalizar_ot, verificar_estado_ot
from .service_operaciones import create_operacion, get_operacion, gets_operaciones_by_ot, update_operacion, delete_operacion, finalizar_operacion
from .service_operaciones import create_reporte_tiempo, get_reporte_tiempo, gets_reportes_tiempo_by_operacion, update_reporte_tiempo, delete_reporte_tiempo, calcular_horas_totales_operacion
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ot",
    tags=["ot"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# ===== Rutas de OT =====

@router.post("/", response_model=OtRead, status_code=status.HTTP_201_CREATED)
async def routes_post_ot(ot: OtCreate, db: Session = Depends(get_db)):
    if ot.id_trabajo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo id_trabajo es requerido")
    try:
        ot_model = OtModel(**ot.model_dump(exclude_unset=True))
        db_ot = create_ot(db=db, ot=ot_model)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al crear OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el registro: {str(e)}")


@router.get("/id/{id}", response_model=OtRead)
async def routes_get_ot_id(id: int, db: Session = Depends(get_db)):
    try:
        db_ot = get_ot(db, id)
        if not db_ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada")
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al obtener OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")


@router.get("/", response_model=List[OtRead])
async def routes_gets_ot_all(
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        db_ot = gets_ot(db)
        if not db_ot:
            return []
        
        # Filtrar por estado si se proporciona
        if estado:
            db_ot = [ot for ot in db_ot if ot.estado == estado]
            
        return [OtRead.model_validate(ot) for ot in db_ot]
    except Exception as e:
        logger.error(f"Error al obtener registros de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")


@router.delete("/id/{id}", response_model=OtRead)
async def routes_delete_ot_id(id: int, db: Session = Depends(get_db)):
    try:
        resultado_ot = get_ot(db, id)
        if not resultado_ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada")
        db_ot = delete_ot(db, id)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al eliminar OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")


@router.put("/id/{id}", response_model=OtRead)
async def routes_update_ot(id: int, ot: OtUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando OT con id = {id}")
    try:
        ot_data = ot.model_dump(exclude_unset=True)
        db_ot = update_ot(db=db, id=id, ot_data=ot_data)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al actualizar OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")


@router.post("/id/{id}/finalizar", response_model=OtRead)
async def routes_finalizar_ot(id: int, db: Session = Depends(get_db)):
    try:
        db_ot = finalizar_ot(db, id)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al finalizar OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al finalizar la OT: {str(e)}")


# ===== Rutas de Operaciones =====

@router.post("/operaciones", response_model=OperacionRead, status_code=status.HTTP_201_CREATED)
async def routes_post_operacion(operacion: OperacionCreate, db: Session = Depends(get_db)):
    if operacion.ot_id is None or operacion.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos ot_id y descripcion son requeridos")
    try:
        operacion_model = OperacionModel(**operacion.model_dump(exclude_unset=True))
        db_operacion = create_operacion(db=db, operacion=operacion_model)
        return OperacionRead.model_validate(db_operacion)
    except Exception as e:
        logger.error(f"Error al crear operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear la operación: {str(e)}")


@router.get("/operaciones/id/{id}", response_model=OperacionRead)
async def routes_get_operacion_id(id: int, db: Session = Depends(get_db)):
    try:
        db_operacion = get_operacion(db, id)
        if not db_operacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operación no encontrada")
        return OperacionRead.model_validate(db_operacion)
    except Exception as e:
        logger.error(f"Error al obtener operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la operación: {str(e)}")


@router.get("/id/{ot_id}/operaciones", response_model=List[OperacionRead])
async def routes_gets_operaciones_by_ot(ot_id: int, db: Session = Depends(get_db)):
    try:
        db_operaciones = gets_operaciones_by_ot(db, ot_id)
        return [OperacionRead.model_validate(op) for op in db_operaciones]
    except Exception as e:
        logger.error(f"Error al obtener operaciones: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener las operaciones: {str(e)}")


@router.put("/operaciones/id/{id}", response_model=OperacionRead)
async def routes_update_operacion(id: int, operacion: OperacionUpdate, db: Session = Depends(get_db)):
    try:
        operacion_data = operacion.model_dump(exclude_unset=True)
        db_operacion = update_operacion(db=db, id=id, operacion_data=operacion_data)
        return OperacionRead.model_validate(db_operacion)
    except Exception as e:
        logger.error(f"Error al actualizar operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar la operación: {str(e)}")


@router.delete("/operaciones/id/{id}", response_model=OperacionRead)
async def routes_delete_operacion(id: int, db: Session = Depends(get_db)):
    try:
        db_operacion = delete_operacion(db, id)
        return OperacionRead.model_validate(db_operacion)
    except Exception as e:
        logger.error(f"Error al eliminar operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar la operación: {str(e)}")


@router.post("/operaciones/id/{id}/finalizar", response_model=OperacionRead)
async def routes_finalizar_operacion(id: int, db: Session = Depends(get_db)):
    try:
        db_operacion = finalizar_operacion(db, id)
        return OperacionRead.model_validate(db_operacion)
    except Exception as e:
        logger.error(f"Error al finalizar operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al finalizar la operación: {str(e)}")


# ===== Rutas de Reportes de Tiempo =====

@router.post("/tiempos", response_model=ReporteTiempoRead, status_code=status.HTTP_201_CREATED)
async def routes_post_reporte_tiempo(reporte: ReporteTiempoCreate, db: Session = Depends(get_db)):
    if reporte.operacion_id is None or reporte.horas is None or reporte.usuario is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos operacion_id, horas y usuario son requeridos")
    try:
        reporte_model = ReporteTiempoModel(**reporte.model_dump(exclude_unset=True))
        db_reporte = create_reporte_tiempo(db=db, reporte_tiempo=reporte_model)
        return ReporteTiempoRead.model_validate(db_reporte)
    except Exception as e:
        logger.error(f"Error al crear reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el reporte de tiempo: {str(e)}")


@router.post("/tiempos/continuar", response_model=ReporteTiempoRead, status_code=status.HTTP_201_CREATED)
async def routes_post_reporte_tiempo_continuar(
    reporte: ReporteTiempoCreate, 
    continuar_iteracion: bool = Query(True, description="Indica si se desea continuar con la iteración"),
    db: Session = Depends(get_db)
):
    if reporte.operacion_id is None or reporte.horas is None or reporte.usuario is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos operacion_id, horas y usuario son requeridos")
    try:
        reporte_model = ReporteTiempoModel(**reporte.model_dump(exclude_unset=True))
        db_reporte = create_reporte_tiempo(db=db, reporte_tiempo=reporte_model, continuar_iteracion=continuar_iteracion)
        return ReporteTiempoRead.model_validate(db_reporte)
    except Exception as e:
        logger.error(f"Error al crear reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el reporte de tiempo: {str(e)}")


@router.get("/tiempos/id/{id}", response_model=ReporteTiempoRead)
async def routes_get_reporte_tiempo_id(id: int, db: Session = Depends(get_db)):
    try:
        db_reporte = get_reporte_tiempo(db, id)
        if not db_reporte:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte de tiempo no encontrado")
        return ReporteTiempoRead.model_validate(db_reporte)
    except Exception as e:
        logger.error(f"Error al obtener reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el reporte de tiempo: {str(e)}")


@router.get("/operaciones/id/{operacion_id}/tiempos", response_model=List[ReporteTiempoRead])
async def routes_gets_reportes_tiempo_by_operacion(operacion_id: int, db: Session = Depends(get_db)):
    try:
        db_reportes = gets_reportes_tiempo_by_operacion(db, operacion_id)
        return [ReporteTiempoRead.model_validate(r) for r in db_reportes]
    except Exception as e:
        logger.error(f"Error al obtener reportes de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los reportes de tiempo: {str(e)}")


@router.put("/tiempos/id/{id}", response_model=ReporteTiempoRead)
async def routes_update_reporte_tiempo(id: int, reporte: ReporteTiempoUpdate, db: Session = Depends(get_db)):
    try:
        reporte_data = reporte.model_dump(exclude_unset=True)
        db_reporte = update_reporte_tiempo(db=db, id=id, reporte_data=reporte_data)
        return ReporteTiempoRead.model_validate(db_reporte)
    except Exception as e:
        logger.error(f"Error al actualizar reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el reporte de tiempo: {str(e)}")


@router.delete("/tiempos/id/{id}", response_model=ReporteTiempoRead)
async def routes_delete_reporte_tiempo(id: int, db: Session = Depends(get_db)):
    try:
        db_reporte = delete_reporte_tiempo(db, id)
        return ReporteTiempoRead.model_validate(db_reporte)
    except Exception as e:
        logger.error(f"Error al eliminar reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el reporte de tiempo: {str(e)}")


@router.get("/operaciones/id/{operacion_id}/horas", response_model=float)
async def routes_get_horas_totales_operacion(operacion_id: int, db: Session = Depends(get_db)):
    try:
        total_horas = calcular_horas_totales_operacion(db, operacion_id)
        return total_horas
    except Exception as e:
        logger.error(f"Error al calcular horas totales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al calcular las horas totales: {str(e)}")


# ===== Rutas de Vistas =====

@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open(f"static/app_stock/ot/ot.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la pagina HTML: {str(e)}")
