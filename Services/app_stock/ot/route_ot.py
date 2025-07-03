from __future__ import annotations

# Asegurar que las anotaciones de tipo se evalúen correctamente en tiempo de ejecución

# Imports estándar
import logging
from typing import List, Optional, Dict, Any

# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.db.database import get_db
from sql_app.Services.app_stock.ot.model_ot import OT as OtModel, Operacion as OperacionModel, ReporteTiempo as ReporteTiempoModel, OTMaterial as OTMaterialModel
from sql_app.Services.app_stock.ot.schema_ot import (
    OT as OtRead,
    OTCreate,
    OTUpdate,
    Operacion as OperacionRead,
    OperacionCreate,
    OperacionUpdate,
    ReporteTiempo as ReporteTiempoRead,
    ReporteTiempoCreate,
    ReporteTiempoUpdate,
    OTMaterial as OTMaterialRead,
    OTMaterialCreate,
    OTMaterialUpdate,
    OTMaterialConsumo
)
from sql_app.Services.app_stock.ot.service_ot import (
    create_ot,
    delete_ot,
    finalizar_ot,
    get_ot,
    gets_ot,
    update_ot,
    verificar_estado_ot,
    calcular_progreso_ot,
    actualizar_estado_ot_automatico,
    puede_modificar_ot
)
from sql_app.Services.app_stock.ot.service_operaciones import (
    calcular_horas_totales_operacion,
    create_operacion,
    create_reporte_tiempo,
    delete_operacion,
    delete_reporte_tiempo,
    finalizar_operacion,
    get_operacion,
    get_reporte_tiempo,
    gets_operaciones_by_ot,
    gets_reportes_tiempo_by_operacion,
    update_operacion,
    update_reporte_tiempo
)
from sql_app.Services.app_stock.ot.service_materiales import (
    create_ot_material,
    get_ot_material,
    get_materiales_by_ot,
    planificar_materiales_ot,
    consumir_material_ot,
    devolver_material_ot,
    get_resumen_materiales_ot,
    validar_disponibilidad_material
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ot",
    tags=["ot"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# ===== Rutas de OT =====

@router.post("/", response_model=OtRead, status_code=status.HTTP_201_CREATED)
async def routes_post_ot(ot: OTCreate, db: Session = Depends(get_db)):
    if ot.id_trabajo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo id_trabajo es requerido")
    try:
        # Crear un objeto OT básico para pasarlo a create_ot
        ot_obj = OtModel()
        ot_obj.numero = ot.numero
        ot_obj.fecha = ot.fecha
        ot_obj.cliente = ot.cliente
        ot_obj.tipo = ot.tipo
        ot_obj.tecnico = ot.tecnico
        ot_obj.descripcion = ot.descripcion
        ot_obj.id_deposito = ot.id_deposito
        ot_obj.estado = ot.estado
        ot_obj.id_trabajo = ot.id_trabajo
        ot_obj.titulo = ot.titulo
        ot_obj.area = ot.area
        ot_obj.personal = ot.personal
        ot_obj.tiempo_estimado = ot.tiempo_estimado
        
        db_ot = create_ot(db=db, ot=ot_obj)
        
        # Procesar tareas asociadas
        if ot.tareas:
            logger.info(f"Procesando {len(ot.tareas)} tareas")
            for i, tarea in enumerate(ot.tareas):
                logger.info(f"Procesando tarea {i}: {tarea}")
                tarea_model = OperacionModel(
                    ot_id=db_ot.id,
                    descripcion=tarea.descripcion,
                    responsable=tarea.responsable,
                    tiempo_estimado=tarea.tiempo_estimado,
                    orden=tarea.orden,
                    estado=tarea.estado
                )
                create_operacion(db=db, operacion=tarea_model)

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


@router.get("/list", response_model=List[OtRead])
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
async def routes_update_ot(id: int, ot: OTUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando OT con id = {id}")
    try:
        # Actualizar la OT (excluir el campo 'tareas' que no pertenece al modelo)
        ot_data = ot.model_dump(exclude_unset=True, exclude={'tareas'})
        db_ot = update_ot(db=db, id=id, ot_data=ot_data)

        # Procesar tareas asociadas
        if ot.tareas:
            for tarea in ot.tareas:
                if tarea.id:
                    # Actualizar tarea existente
                    tarea_data = {
                        "descripcion": tarea.descripcion,
                        "responsable": tarea.responsable,
                        "tiempo_estimado": tarea.tiempo_estimado,
                        "orden": tarea.orden,
                        "estado": tarea.estado
                    }
                    # Filtrar valores None
                    tarea_data = {k: v for k, v in tarea_data.items() if v is not None}
                    update_operacion(db=db, id=tarea.id, operacion_data=tarea_data)
                else:
                    # Crear nueva tarea
                    tarea_model = OperacionModel(
                        ot_id=id,
                        descripcion=tarea.descripcion,
                        responsable=tarea.responsable,
                        tiempo_estimado=tarea.tiempo_estimado,
                        orden=tarea.orden,
                        estado=tarea.estado
                    )
                    create_operacion(db=db, operacion=tarea_model)

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


# ===== Rutas de Operaciones/Tareas =====

@router.get("/id/{ot_id}/tareas", response_model=List[OperacionRead])
async def get_tareas_ot(ot_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todas las tareas (operaciones) de una OT específica.
    """
    try:
        # Verificar que la OT existe
        ot = get_ot(db, ot_id)
        if not ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada")
        
        # Obtener las operaciones de la OT
        operaciones = gets_operaciones_by_ot(db, ot_id)
        return [OperacionRead.model_validate(op) for op in operaciones]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener tareas de OT {ot_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener las tareas: {str(e)}")

@router.post("/id/{ot_id}/tareas", response_model=OperacionRead, status_code=status.HTTP_201_CREATED)
async def crear_tarea_ot(ot_id: int, operacion: OperacionCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva tarea (operación) para una OT específica.
    """
    try:
        # Verificar que la OT existe
        ot = get_ot(db, ot_id)
        if not ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada")
        
        # Verificar que la OT se puede modificar
        if not puede_modificar_ot(db, ot_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pueden agregar tareas a una OT finalizada")
        
        # Asegurar que el ot_id coincida
        operacion.ot_id = ot_id
        
        # Crear la operación
        nueva_operacion = create_operacion(db, operacion)
        
        # Actualizar estado automático de la OT
        actualizar_estado_ot_automatico(db, ot_id)
        
        return OperacionRead.model_validate(nueva_operacion)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear tarea para OT {ot_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear la tarea: {str(e)}")

@router.put("/tareas/{operacion_id}", response_model=OperacionRead)
async def actualizar_tarea(operacion_id: int, operacion_update: OperacionUpdate, db: Session = Depends(get_db)):
    """
    Actualiza una tarea (operación) específica.
    """
    try:
        # Obtener la operación actual
        operacion_actual = get_operacion(db, operacion_id)
        if not operacion_actual:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
        
        # Verificar que la OT se puede modificar
        if not puede_modificar_ot(db, operacion_actual.ot_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pueden modificar tareas de una OT finalizada")
        
        # Actualizar la operación
        operacion_actualizada = update_operacion(db, operacion_id, operacion_update)
        
        # Actualizar estado automático de la OT
        actualizar_estado_ot_automatico(db, operacion_actual.ot_id)
        
        return OperacionRead.model_validate(operacion_actualizada)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar tarea {operacion_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar la tarea: {str(e)}")

@router.delete("/tareas/{operacion_id}")
async def eliminar_tarea(operacion_id: int, db: Session = Depends(get_db)):
    """
    Elimina una tarea (operación) específica.
    """
    try:
        # Obtener la operación para conocer la OT
        operacion = get_operacion(db, operacion_id)
        if not operacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
        
        ot_id = operacion.ot_id
        
        # Verificar que la OT se puede modificar
        if not puede_modificar_ot(db, ot_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pueden eliminar tareas de una OT finalizada")
        
        # Eliminar la operación
        delete_operacion(db, operacion_id)
        
        # Actualizar estado automático de la OT
        actualizar_estado_ot_automatico(db, ot_id)
        
        return {"message": "Tarea eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar tarea {operacion_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar la tarea: {str(e)}")

# ===== Rutas de Vistas =====

# Ruta para la página principal de OT (sin /pagina)
@router.get("/")
async def get_pagina_ot_principal(
    request: Request,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Devuelve la página HTML principal de Órdenes de Trabajo o JSON según el header Accept.
    Accessible vía /app_stock/ot/
    """
    # Verificar si es una solicitud de API (JSON) o página web (HTML)
    accept_header = request.headers.get("accept", "")
    
    if "application/json" in accept_header or "text/html" not in accept_header:
        # Es una solicitud API, devolver JSON
        try:
            db_ot = gets_ot(db)
            if not db_ot:
                return []
            
            # Filtrar por estado si se proporciona
            if estado:
                db_ot = [ot for ot in db_ot if ot.estado == estado]
            
            # Calcular progreso para cada OT
            ot_list = []
            for ot in db_ot:
                ot_dict = OtRead.model_validate(ot).model_dump()
                ot_dict['progreso'] = calcular_progreso_ot(db, ot.id)
                ot_list.append(ot_dict)
                
            return ot_list
        except Exception as e:
            logger.error(f"Error al obtener registros de OT: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
    else:
        # Es una solicitud de página web, devolver HTML
        try:
            with open(f"sql_app/static/app_stock/ot/ot.html", "r", encoding="utf-8") as file:
                html_content = file.read()
            return HTMLResponse(content=html_content)
        except Exception as e:
            logger.error(f"Error al obtener la pagina HTML principal de OT: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la pagina HTML: {str(e)}")

@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open(f"sql_app/static/app_stock/ot/ot.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la pagina HTML: {str(e)}")

@router.get("/materiales/pagina", response_class=HTMLResponse)
async def get_pagina_materiales():
    """
    Devuelve la página HTML para la gestión de materiales de OT.
    """
    try:
        with open(f"sql_app/static/app_stock/ot/materiales_ot.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina de materiales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la pagina de materiales: {str(e)}")

@router.get("/{ot_id}/materiales", response_class=HTMLResponse)
async def get_pagina_materiales_ot(ot_id: int, db: Session = Depends(get_db)):
    """
    Devuelve la página HTML para la gestión de materiales de una OT específica.
    Verifica que la OT existe antes de mostrar la página.
    """
    try:
        # Verificar que la OT existe
        ot = get_ot(db, ot_id)
        if not ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Orden de trabajo con ID {ot_id} no encontrada")
        
        # Leer el archivo HTML
        with open(f"sql_app/static/app_stock/ot/materiales_ot.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        
        # Inyectar el ID de la OT en el HTML para que el frontend lo pueda usar
        html_content = html_content.replace(
            '<body', 
            f'<body data-ot-id="{ot_id}" data-ot-numero="{ot.numero}" data-ot-cliente="{ot.cliente}"'
        )
        
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener la pagina de materiales para OT {ot_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la pagina de materiales: {str(e)}")


# ===== Rutas de Materiales de OT =====

@router.post("/id/{ot_id}/materiales/planificar", response_model=Dict[str, Any])
async def routes_planificar_materiales_ot(
    ot_id: int,
    materiales: List[OTMaterialCreate],
    db: Session = Depends(get_db)
):
    """
    Planifica los materiales que se van a utilizar en una OT.
    Permite asignar qué materiales y en qué cantidades se espera usar.
    """
    try:
        # Convertir a formato dict para el servicio
        materiales_data = [material.model_dump() for material in materiales]
        
        # Validar disponibilidad de cada material
        validaciones = []
        for material_data in materiales_data:
            validacion = validar_disponibilidad_material(
                db, 
                material_data["codigo_art"], 
                material_data["id_deposito"], 
                material_data["cantidad_planificada"]
            )
            validacion["codigo_art"] = material_data["codigo_art"]
            validaciones.append(validacion)
        
        # Planificar materiales
        materiales_creados = planificar_materiales_ot(db, ot_id, materiales_data)
        
        return {
            "mensaje": f"Materiales planificados exitosamente para OT #{ot_id}",
            "ot_id": ot_id,
            "materiales_planificados": len(materiales_creados),
            "validaciones_stock": validaciones,
            "detalles": [
                {
                    "id": m.id,
                    "codigo_art": m.codigo_art,
                    "id_deposito": m.id_deposito,
                    "cantidad_planificada": m.cantidad_planificada,
                    "estado": m.estado
                } for m in materiales_creados
            ]
        }
        
    except Exception as e:
        logger.error(f"Error al planificar materiales de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/id/{ot_id}/materiales", response_model=Dict[str, Any])
async def routes_get_materiales_ot(
    ot_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los materiales asociados a una OT (planificados y utilizados).
    """
    try:
        resumen = get_resumen_materiales_ot(db, ot_id)
        return resumen
        
    except Exception as e:
        logger.error(f"Error al obtener materiales de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/materiales/{material_id}/consumir", response_model=Dict[str, Any])
async def routes_consumir_material(
    material_id: int,
    datos_consumo: OTMaterialConsumo,
    db: Session = Depends(get_db)
):
    """
    Registra el consumo de un material específico y actualiza el stock.
    """
    try:
        resultado = consumir_material_ot(
            db, 
            material_id, 
            datos_consumo.cantidad_utilizada,
            datos_consumo.usuario_consumo,
            datos_consumo.observacion
        )
        
        return {
            "mensaje": "Material consumido exitosamente",
            **resultado
        }
        
    except Exception as e:
        logger.error(f"Error al consumir material: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/materiales/{material_id}/devolver", response_model=Dict[str, Any])
async def routes_devolver_material(
    material_id: int,
    cantidad_devuelta: float,
    usuario_devolucion: str,
    observacion: str = None,
    db: Session = Depends(get_db)
):
    """
    Devuelve material no utilizado al stock.
    """
    try:
        resultado = devolver_material_ot(
            db, 
            material_id, 
            cantidad_devuelta,
            usuario_devolucion,
            observacion
        )
        
        return {
            "mensaje": "Material devuelto exitosamente",
            **resultado
        }
        
    except Exception as e:
        logger.error(f"Error al devolver material: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/materiales/{material_id}", response_model=OTMaterialRead)
async def routes_get_material_detalle(
    material_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un material específico de OT.
    """
    try:
        material = get_ot_material(db, material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado")
        
        return OTMaterialRead.model_validate(material)
        
    except Exception as e:
        logger.error(f"Error al obtener detalle de material: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/materiales/validar-stock/{codigo_art}/{id_deposito}", response_model=Dict[str, Any])
async def routes_validar_stock_material(
    codigo_art: int,
    id_deposito: int,
    cantidad_requerida: float,
    db: Session = Depends(get_db)
):
    """
    Valida si hay suficiente stock disponible para un material.
    """
    try:
        validacion = validar_disponibilidad_material(db, codigo_art, id_deposito, cantidad_requerida)
        return validacion
        
    except Exception as e:
        logger.error(f"Error al validar stock de material: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Endpoint de Debug =====

@router.post("/debug", status_code=status.HTTP_201_CREATED)
async def debug_post_ot(request: Request):
    """Endpoint de debug para ver exactamente qué se está enviando"""
    try:
        body = await request.body()
        logger.info(f"Raw body: {body.decode()}")
        
        import json
        data = json.loads(body.decode())
        logger.info(f"Parsed JSON: {data}")
        
        return {"message": "Debug successful", "data": data}
    except Exception as e:
        logger.error(f"Error en debug: {e}")
        return {"error": str(e)}
