
# Imports de bibliotecas estándar
import datetime
import logging
from typing import Any, Dict, List, Optional

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Imports del proyecto
from Services.app_stock.ot.model_ot import Operacion, ReporteTiempo

logger = logging.getLogger(__name__)

# ===== Servicios de Operaciones =====

def create_operacion(db: Session, operacion: Operacion) -> Operacion:
    """
    Crea una nueva operación asociada a una OT.
    """
    try:
        # Preparar los datos para la consulta
        operacion_data = {}
        
        fields = ['ot_id', 'descripcion', 'tiempo_estimado', 'responsable', 'estado', 'orden']
        
        for field in fields:
            if hasattr(operacion, field) and getattr(operacion, field) is not None:
                operacion_data[field] = getattr(operacion, field)
        
        # Si no se proporciona un orden, asignar el siguiente
        if 'orden' not in operacion_data or operacion_data['orden'] is None:
            query_max_orden = text("""
                SELECT MAX(orden) FROM ot_operaciones WHERE ot_id = :ot_id
            """)
            max_orden = db.execute(query_max_orden, {"ot_id": operacion_data['ot_id']}).scalar()
            operacion_data['orden'] = 1 if max_orden is None else max_orden + 1
        
        # Construir la consulta SQL INSERT
        fields_str = ", ".join(operacion_data.keys())
        values_str = ", ".join([f":{field}" for field in operacion_data.keys()])
        
        output_fields = "id, ot_id, descripcion, tiempo_estimado, responsable, estado, orden"
        
        query = text(f"""
            INSERT INTO ot_operaciones ({fields_str})
            OUTPUT INSERTED.{output_fields.replace(", ", ", INSERTED.")}
            VALUES ({values_str})
        """)
        
        # Ejecutar la consulta y obtener el registro insertado
        result = db.execute(query, operacion_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La operación no se pudo crear"
            )
        
        # Crear un nuevo objeto Operacion con los valores devueltos
        new_operacion = Operacion()
        new_operacion.id = row[0]
        new_operacion.ot_id = row[1]
        new_operacion.descripcion = row[2]
        new_operacion.tiempo_estimado = row[3]
        new_operacion.responsable = row[4]
        new_operacion.estado = row[5]
        new_operacion.orden = row[6]
        
        # Actualizar estado de OT a "en_proceso" si es la primera operación
        if operacion_data.get('orden') == 1:
            update_ot_query = text("""
                UPDATE ot
                SET estado = 'en_proceso', fecha_inicio = :fecha_inicio
                WHERE id = :ot_id AND estado = 'pendiente'
            """)
            db.execute(update_ot_query, {
                "ot_id": new_operacion.ot_id,
                "fecha_inicio": datetime.datetime.now()
            })
            db.commit()
        
        return new_operacion
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear operación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la operación: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear operación: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_operacion(db: Session, id: int) -> Optional[Operacion]:
    """
    Obtiene una operación por su ID, incluyendo los reportes de tiempo asociados.
    """
    try:
        # Consulta principal para obtener la operación
        operacion_query = text("""
            SELECT id, ot_id, descripcion, tiempo_estimado, responsable, estado, orden
            FROM ot_operaciones 
            WHERE id = :id
        """)
        
        operacion_result = db.execute(operacion_query, {"id": id}).first()
        
        if not operacion_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operación no encontrada.")
        
        # Crear el objeto Operacion
        operacion = Operacion()
        operacion.id = operacion_result[0]
        operacion.ot_id = operacion_result[1]
        operacion.descripcion = operacion_result[2]
        operacion.tiempo_estimado = operacion_result[3]
        operacion.responsable = operacion_result[4]
        operacion.estado = operacion_result[5]
        operacion.orden = operacion_result[6]
        
        # Obtener reportes de tiempo asociados
        reportes_query = text("""
            SELECT id, operacion_id, fecha, horas, descripcion, usuario
            FROM ot_reportes_tiempo
            WHERE operacion_id = :operacion_id
            ORDER BY fecha
        """)
        
        reportes_result = db.execute(reportes_query, {"operacion_id": id}).fetchall()
        
        operacion.reportes_tiempo = []
        for rep_row in reportes_result:
            reporte = ReporteTiempo()
            reporte.id = rep_row[0]
            reporte.operacion_id = rep_row[1]
            reporte.fecha = rep_row[2]
            reporte.horas = rep_row[3]
            reporte.descripcion = rep_row[4]
            reporte.usuario = rep_row[5]
            operacion.reportes_tiempo.append(reporte)
        
        return operacion
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la operación: {str(e)}")

def gets_operaciones_by_ot(db: Session, ot_id: int) -> List[Operacion]:
    """
    Obtiene todas las operaciones asociadas a una OT.
    """
    try:
        operaciones_query = text("""
            SELECT id, ot_id, descripcion, tiempo_estimado, responsable, estado, orden
            FROM ot_operaciones
            WHERE ot_id = :ot_id
            ORDER BY orden
        """)
        
        operaciones_result = db.execute(operaciones_query, {"ot_id": ot_id}).fetchall()
        
        operaciones = []
        for op_row in operaciones_result:
            operacion = Operacion()
            operacion.id = op_row[0]
            operacion.ot_id = op_row[1]
            operacion.descripcion = op_row[2]
            operacion.tiempo_estimado = op_row[3]
            operacion.responsable = op_row[4]
            operacion.estado = op_row[5]
            operacion.orden = op_row[6]
            
            # Obtener reportes de tiempo para esta operación
            reportes_query = text("""
                SELECT id, operacion_id, fecha, horas, descripcion, usuario
                FROM ot_reportes_tiempo
                WHERE operacion_id = :operacion_id
                ORDER BY fecha
            """)
            
            reportes_result = db.execute(reportes_query, {"operacion_id": operacion.id}).fetchall()
            
            operacion.reportes_tiempo = []
            for rep_row in reportes_result:
                reporte = ReporteTiempo()
                reporte.id = rep_row[0]
                reporte.operacion_id = rep_row[1]
                reporte.fecha = rep_row[2]
                reporte.horas = rep_row[3]
                reporte.descripcion = rep_row[4]
                reporte.usuario = rep_row[5]
                operacion.reportes_tiempo.append(reporte)
            
            operaciones.append(operacion)
        
        return operaciones
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener operaciones: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener las operaciones: {str(e)}")

def update_operacion(db: Session, id: int, operacion_data: Dict[str, Any]) -> Operacion:
    """
    Actualiza una operación existente.
    """
    logger.info(f"Actualizando operación con id = {id}")
    try:
        # Verificar que el registro existe y obtener datos actuales
        operacion = get_operacion(db, id)
        
        # Eliminar campos no actualizables
        operacion_data_copy = operacion_data.copy()
        if 'id' in operacion_data_copy:
            del operacion_data_copy['id']
        if 'ot_id' in operacion_data_copy:
            del operacion_data_copy['ot_id']
        
        # Si no hay campos para actualizar, retornar el registro actual
        if not operacion_data_copy:
            return operacion
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in operacion_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ot_operaciones
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.ot_id, INSERTED.descripcion, 
                   INSERTED.tiempo_estimado, INSERTED.responsable, INSERTED.estado, INSERTED.orden
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = operacion_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar la operación.")
        
        # Actualizar el objeto con los datos nuevos
        updated_operacion = Operacion()
        updated_operacion.id = result[0]
        updated_operacion.ot_id = result[1]
        updated_operacion.descripcion = result[2]
        updated_operacion.tiempo_estimado = result[3]
        updated_operacion.responsable = result[4]
        updated_operacion.estado = result[5]
        updated_operacion.orden = result[6]
        
        # Si se cambió el estado a "finalizada", verificar si todas las operaciones están finalizadas
        if operacion_data_copy.get('estado') == 'finalizada':
            from Services.app_stock.ot.service_ot import verificar_estado_ot
            todas_finalizadas = verificar_estado_ot(db, updated_operacion.ot_id)
            
            if todas_finalizadas:
                # Actualizar estado de OT
                update_ot_query = text("""
                    UPDATE ot
                    SET estado = 'finalizada', fecha_fin = :fecha_fin
                    WHERE id = :ot_id AND estado = 'en_proceso'
                """)
                db.execute(update_ot_query, {
                    "ot_id": updated_operacion.ot_id,
                    "fecha_fin": datetime.datetime.now()
                })
                db.commit()
        
        # Cargar reportes de tiempo
        updated_operacion = get_operacion(db, id)
        
        return updated_operacion
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar la operación: {str(e)}")

def delete_operacion(db: Session, id: int) -> Operacion:
    """
    Elimina una operación y sus reportes de tiempo asociados.
    """
    try:
        # Primero obtenemos la operación para devolver sus datos
        operacion = get_operacion(db, id)
        
        # Eliminar reportes de tiempo asociados
        reportes_delete_query = text("""
            DELETE FROM ot_reportes_tiempo
            WHERE operacion_id = :operacion_id
        """)
        db.execute(reportes_delete_query, {"operacion_id": id})
        
        # Eliminar la operación
        operacion_delete_query = text("""
            DELETE FROM ot_operaciones
            WHERE id = :id
        """)
        db.execute(operacion_delete_query, {"id": id})
        
        # Reordenar las operaciones restantes
        reordenar_query = text("""
            WITH NumberedRows AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY orden) AS NewOrden
                FROM ot_operaciones
                WHERE ot_id = :ot_id
            )
            UPDATE ot_operaciones
            SET orden = nr.NewOrden
            FROM ot_operaciones op
            INNER JOIN NumberedRows nr ON op.id = nr.id
        """)
        db.execute(reordenar_query, {"ot_id": operacion.ot_id})
        
        db.commit()
        return operacion
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar la operación: {str(e)}")

# ===== Servicios de Reportes de Tiempo =====

def create_reporte_tiempo(db: Session, reporte_tiempo: ReporteTiempo, continuar_iteracion: bool = True) -> ReporteTiempo:
    """
    Crea un nuevo reporte de tiempo para una operación.
    
    Parameters:
    - db: Session de SQLAlchemy
    - reporte_tiempo: Objeto con los datos del reporte
    - continuar_iteracion: Indica si se desea continuar con la iteración después de registrar el tiempo
    
    Returns:
    - ReporteTiempo: El objeto de reporte de tiempo creado
    """
    try:
        # Preparar los datos para la consulta
        reporte_data = {}
        
        fields = ['operacion_id', 'fecha', 'horas', 'descripcion', 'usuario']
        
        for field in fields:
            if hasattr(reporte_tiempo, field) and getattr(reporte_tiempo, field) is not None:
                reporte_data[field] = getattr(reporte_tiempo, field)
        
        # Si no se proporciona una fecha, utilizar la fecha actual
        if 'fecha' not in reporte_data or reporte_data['fecha'] is None:
            reporte_data['fecha'] = datetime.datetime.now()
        
        # Construir la consulta SQL INSERT
        fields_str = ", ".join(reporte_data.keys())
        values_str = ", ".join([f":{field}" for field in reporte_data.keys()])
        
        output_fields = "id, operacion_id, fecha, horas, descripcion, usuario"
        
        query = text(f"""
            INSERT INTO ot_reportes_tiempo ({fields_str})
            OUTPUT INSERTED.{output_fields.replace(", ", ", INSERTED.")}
            VALUES ({values_str})
        """)
        
        # Ejecutar la consulta y obtener el registro insertado
        result = db.execute(query, reporte_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El reporte de tiempo no se pudo crear"
            )
        
        # Crear un nuevo objeto ReporteTiempo con los valores devueltos
        new_reporte = ReporteTiempo()
        new_reporte.id = row[0]
        new_reporte.operacion_id = row[1]
        new_reporte.fecha = row[2]
        new_reporte.horas = row[3]
        new_reporte.descripcion = row[4]
        new_reporte.usuario = row[5]
        
        # Si no se desea continuar con la iteración, actualizar el estado de la operación
        if not continuar_iteracion:
            # Obtener la operación asociada
            operacion_query = text("""
                SELECT id, ot_id FROM ot_operaciones 
                WHERE id = :operacion_id
            """)
            operacion_result = db.execute(operacion_query, {"operacion_id": new_reporte.operacion_id}).first()
            
            if operacion_result:
                # Actualizar el estado de la operación a "finalizada"
                update_operacion(db, operacion_result[0], {"estado": "finalizada"})
                logger.info(f"Operación {operacion_result[0]} marcada como finalizada por decisión del usuario")
        
        return new_reporte
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear reporte de tiempo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el reporte de tiempo: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear reporte de tiempo: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_reporte_tiempo(db: Session, id: int) -> Optional[ReporteTiempo]:
    """
    Obtiene un reporte de tiempo por su ID.
    """
    try:
        reporte_query = text("""
            SELECT id, operacion_id, fecha, horas, descripcion, usuario
            FROM ot_reportes_tiempo 
            WHERE id = :id
        """)
        
        reporte_result = db.execute(reporte_query, {"id": id}).first()
        
        if not reporte_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte de tiempo no encontrado.")
        
        # Crear el objeto ReporteTiempo
        reporte = ReporteTiempo()
        reporte.id = reporte_result[0]
        reporte.operacion_id = reporte_result[1]
        reporte.fecha = reporte_result[2]
        reporte.horas = reporte_result[3]
        reporte.descripcion = reporte_result[4]
        reporte.usuario = reporte_result[5]
        
        return reporte
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el reporte de tiempo: {str(e)}")

def gets_reportes_tiempo_by_operacion(db: Session, operacion_id: int) -> List[ReporteTiempo]:
    """
    Obtiene todos los reportes de tiempo de una operación.
    """
    try:
        reportes_query = text("""
            SELECT id, operacion_id, fecha, horas, descripcion, usuario
            FROM ot_reportes_tiempo
            WHERE operacion_id = :operacion_id
            ORDER BY fecha
        """)
        
        reportes_result = db.execute(reportes_query, {"operacion_id": operacion_id}).fetchall()
        
        reportes = []
        for rep_row in reportes_result:
            reporte = ReporteTiempo()
            reporte.id = rep_row[0]
            reporte.operacion_id = rep_row[1]
            reporte.fecha = rep_row[2]
            reporte.horas = rep_row[3]
            reporte.descripcion = rep_row[4]
            reporte.usuario = rep_row[5]
            reportes.append(reporte)
        
        return reportes
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener reportes de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los reportes de tiempo: {str(e)}")

def update_reporte_tiempo(db: Session, id: int, reporte_data: Dict[str, Any]) -> ReporteTiempo:
    """
    Actualiza un reporte de tiempo existente.
    """
    logger.info(f"Actualizando reporte de tiempo con id = {id}")
    try:
        # Verificar que el registro existe
        reporte = get_reporte_tiempo(db, id)
        
        # Eliminar campos no actualizables
        reporte_data_copy = reporte_data.copy()
        if 'id' in reporte_data_copy:
            del reporte_data_copy['id']
        if 'operacion_id' in reporte_data_copy:
            del reporte_data_copy['operacion_id']
        
        # Si no hay campos para actualizar, devolver el registro actual
        if not reporte_data_copy:
            return reporte
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in reporte_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ot_reportes_tiempo
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.operacion_id, INSERTED.fecha, 
                   INSERTED.horas, INSERTED.descripcion, INSERTED.usuario
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = reporte_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el reporte de tiempo.")
        
        # Actualizar el objeto con los datos nuevos
        updated_reporte = ReporteTiempo()
        updated_reporte.id = result[0]
        updated_reporte.operacion_id = result[1]
        updated_reporte.fecha = result[2]
        updated_reporte.horas = result[3]
        updated_reporte.descripcion = result[4]
        updated_reporte.usuario = result[5]
        
        return updated_reporte
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el reporte de tiempo: {str(e)}")

def delete_reporte_tiempo(db: Session, id: int) -> ReporteTiempo:
    """
    Elimina un reporte de tiempo.
    """
    try:
        # Primero obtenemos el reporte para devolver sus datos
        reporte = get_reporte_tiempo(db, id)
        
        # Eliminar el reporte de tiempo
        reporte_delete_query = text("""
            DELETE FROM ot_reportes_tiempo
            WHERE id = :id
        """)
        db.execute(reporte_delete_query, {"id": id})
        
        db.commit()
        return reporte
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar reporte de tiempo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el reporte de tiempo: {str(e)}")

def calcular_horas_totales_operacion(db: Session, operacion_id: int) -> float:
    """
    Calcula el total de horas reportadas para una operación.
    """
    try:
        query = text("""
            SELECT COALESCE(SUM(horas), 0) FROM ot_reportes_tiempo
            WHERE operacion_id = :operacion_id
        """)
        
        total_horas = db.execute(query, {"operacion_id": operacion_id}).scalar()
        
        return float(total_horas) if total_horas else 0.0
    
    except SQLAlchemyError as e:
        logger.error(f"Error al calcular horas totales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al calcular horas totales: {str(e)}")

def finalizar_operacion(db: Session, operacion_id: int) -> Operacion:
    """
    Marca una operación como finalizada y actualiza el estado de la OT si es necesario.
    """
    try:
        # Obtener la operación
        operacion = get_operacion(db, operacion_id)
        
        # Verificar si ya está finalizada
        if operacion.estado == 'finalizada':
            return operacion
        
        # Actualizar el estado de la operación
        operacion_data = {
            "estado": "finalizada"
        }
        
        # Actualizar la operación y verificar la OT
        updated_operacion = update_operacion(db, operacion_id, operacion_data)
        
        return updated_operacion
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al finalizar operación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al finalizar operación: {str(e)}")