# Imports de bibliotecas estándar
import datetime
import logging
from typing import List, Optional, Dict, Any

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.Services.app_stock.ot.model_ot import OT as Ot, Operacion, ReporteTiempo

logger = logging.getLogger(__name__)

# ===== Funciones de cálculo de progreso =====
def calcular_progreso_ot(db: Session, ot_id: int) -> float:
    """
    Calcula el progreso de una OT basado en el porcentaje de tareas completadas.
    
    Args:
        db: Sesión de base de datos
        ot_id: ID de la OT
        
    Returns:
        float: Porcentaje de progreso (0-100)
    """
    try:
        # Obtener todas las operaciones de la OT
        operaciones = db.query(Operacion).filter(Operacion.ot_id == ot_id).all()
        
        if not operaciones:
            return 0.0
        
        total_operaciones = len(operaciones)
        operaciones_completadas = len([op for op in operaciones if op.estado == "finalizada"])
        
        progreso = (operaciones_completadas / total_operaciones) * 100
        return round(progreso, 1)
        
    except Exception as e:
        logger.error(f"Error al calcular progreso de OT {ot_id}: {e}")
        return 0.0

def actualizar_estado_ot_automatico(db: Session, ot_id: int) -> bool:
    """
    Actualiza automáticamente el estado de una OT basado en el progreso de sus tareas.
    
    Args:
        db: Sesión de base de datos
        ot_id: ID de la OT
        
    Returns:
        bool: True si se actualizó el estado, False en caso contrario
    """
    try:
        ot = db.query(Ot).filter(Ot.id == ot_id).first()
        if not ot:
            return False
            
        progreso = calcular_progreso_ot(db, ot_id)
        
        # Lógica para actualizar estado automáticamente
        nuevo_estado = None
        if progreso == 0:
            nuevo_estado = "planificando"
        elif 0 < progreso < 100:
            nuevo_estado = "ejecutando"
        elif progreso == 100:
            nuevo_estado = "finalizada"
            
        if nuevo_estado and ot.estado != nuevo_estado:
            ot.estado = nuevo_estado
            if nuevo_estado == "ejecutando" and not ot.fecha_inicio:
                ot.fecha_inicio = datetime.datetime.utcnow()
            elif nuevo_estado == "finalizada" and not ot.fecha_fin:
                ot.fecha_fin = datetime.datetime.utcnow()
                
            db.commit()
            logger.info(f"Estado de OT {ot_id} actualizado automáticamente a: {nuevo_estado}")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error al actualizar estado automático de OT {ot_id}: {e}")
        db.rollback()
        return False

def puede_modificar_ot(db: Session, ot_id: int) -> bool:
    """
    Verifica si una OT puede ser modificada basándose en su estado.
    Las OT finalizadas no pueden modificarse.
    
    Args:
        db: Sesión de base de datos
        ot_id: ID de la OT
        
    Returns:
        bool: True si se puede modificar, False si está finalizada
    """
    try:
        ot = db.query(Ot).filter(Ot.id == ot_id).first()
        if not ot:
            return False
            
        return ot.estado != "finalizada"
        
    except Exception as e:
        logger.error(f"Error al verificar si puede modificar OT {ot_id}: {e}")
        return False

# ===== Servicios de OT =====
def create_ot(db: Session, ot: Ot) -> Ot:
    """
    Crea una nueva OT en la base de datos.
    """
    try:
        # Preparar los datos para la consulta
        ot_data = {}
        
        # Excluimos el campo 'id' ya que es autoincremental
        fields = ['id_trabajo', 'area', 'personal', 'tiempo_estimado', 
                  'titulo', 'descripcion', 'estado']
        
        # Agregamos id_deposito solo si tiene un valor válido
        if hasattr(ot, 'id_deposito') and ot.id_deposito is not None:
            # Verificar si el id_deposito existe en la tabla depositos
            deposito_exists = db.execute(
                text("SELECT 1 FROM depositos WHERE id = :id_deposito"),
                {"id_deposito": ot.id_deposito}
            ).scalar() is not None
            
            if deposito_exists:
                fields.append('id_deposito')
            else:
                logger.warning(f"El depósito con id {ot.id_deposito} no existe. Se establecerá como NULL.")
        
        # Asegurarnos de que estado tenga un valor predeterminado
        if not hasattr(ot, 'estado') or ot.estado is None:
            ot.estado = "planificando"
        
        for field in fields:
            if hasattr(ot, field) and getattr(ot, field) is not None:
                ot_data[field] = getattr(ot, field)
        
        # Campos de fecha automáticos
        if not ot_data.get('fecha_creacion'):
            ot_data['fecha_creacion'] = datetime.datetime.now()
            fields.append('fecha_creacion')
        
        # Construir la consulta SQL INSERT
        fields_str = ", ".join(ot_data.keys())
        values_str = ", ".join([f":{field}" for field in ot_data.keys()])
        
        # Encapsular los nombres de columna entre corchetes [] para asegurar compatibilidad
        query = text(f"""
            INSERT INTO ot ({fields_str})
            OUTPUT INSERTED.[id], INSERTED.[id_trabajo], INSERTED.[area], INSERTED.[personal], 
                  INSERTED.[tiempo_estimado], INSERTED.[titulo], INSERTED.[descripcion], 
                  INSERTED.[fecha_creacion], INSERTED.[fecha_inicio], INSERTED.[fecha_fin], 
                  INSERTED.[estado], INSERTED.[id_deposito]
            VALUES ({values_str})
        """)
        
        # Ejecutar la consulta y obtener el registro insertado
        result = db.execute(query, ot_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La OT no se pudo crear"
            )
        
        # Crear un nuevo objeto Ot con los valores devueltos
        new_ot = Ot()
        new_ot.id = row[0]
        new_ot.id_trabajo = row[1]
        new_ot.area = row[2]
        new_ot.personal = row[3]
        new_ot.tiempo_estimado = row[4]
        new_ot.titulo = row[5]
        new_ot.descripcion = row[6]
        new_ot.fecha_creacion = row[7]
        new_ot.fecha_inicio = row[8]
        new_ot.fecha_fin = row[9]
        new_ot.estado = row[10]
        new_ot.id_deposito = row[11]
        
        return new_ot
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear OT: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear OT: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_ot(db: Session, id: int) -> Optional[Ot]:
    """
    Obtiene una OT por su ID, incluyendo las operaciones y reportes de tiempo asociados.
    """
    try:
        # Consulta principal para obtener la OT
        ot_query = text("""
            SELECT id, id_trabajo, area, personal, tiempo_estimado, titulo, descripcion, 
                   fecha_creacion, fecha_inicio, fecha_fin, estado, id_deposito 
            FROM ot 
            WHERE id = :id
        """)
        
        ot_result = db.execute(ot_query, {"id": id}).first()
        
        if not ot_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada.")
        
        # Crear el objeto OT
        ot = Ot()
        ot.id = ot_result[0]
        ot.id_trabajo = ot_result[1]
        ot.area = ot_result[2]
        ot.personal = ot_result[3]
        ot.tiempo_estimado = ot_result[4]
        ot.titulo = ot_result[5]
        ot.descripcion = ot_result[6]
        ot.fecha_creacion = ot_result[7]
        ot.fecha_inicio = ot_result[8]
        ot.fecha_fin = ot_result[9]
        ot.estado = ot_result[10]
        ot.id_deposito = ot_result[11]
        
        # Obtener las operaciones asociadas
        operaciones_query = text("""
            SELECT id, ot_id, descripcion, tiempo_estimado, responsable, estado, orden
            FROM ot_operaciones
            WHERE ot_id = :ot_id
            ORDER BY orden
        """)
        
        operaciones_result = db.execute(operaciones_query, {"ot_id": id}).fetchall()
        
        ot.operaciones = []
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
            
            ot.operaciones.append(operacion)
        
        return ot
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

# Mantenemos los servicios existentes y los actualizamos según sea necesario
def gets_ot(db: Session) -> List[Ot]:
    """
    Obtiene una lista de todos los registros de OT.
    """
    try:
        result = db.execute(
            text("""
                SELECT id, id_trabajo, area, personal, tiempo_estimado, titulo, descripcion, 
                       fecha_creacion, fecha_inicio, fecha_fin, estado, id_deposito 
                FROM ot
                ORDER BY fecha_creacion DESC
            """)
        )
        
        ots = []
        for row in result.fetchall():
            ot = Ot()
            ot.id = row[0]
            ot.id_trabajo = row[1]
            ot.area = row[2]
            ot.personal = row[3]
            ot.tiempo_estimado = row[4]
            ot.titulo = row[5]
            ot.descripcion = row[6]
            ot.fecha_creacion = row[7]
            ot.fecha_inicio = row[8]
            ot.fecha_fin = row[9]
            ot.estado = row[10]
            ot.id_deposito = row[11]
            ots.append(ot)
        
        return ots
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_ot(db: Session, id: int) -> Ot:
    """
    Elimina una OT y todas sus operaciones y reportes asociados.
    """
    try:
        # Primero obtenemos la OT para devolver sus datos después
        ot = get_ot(db, id)
        
        # Eliminar reportes de tiempo asociados a las operaciones de esta OT
        reportes_delete_query = text("""
            DELETE FROM ot_reportes_tiempo
            WHERE operacion_id IN (SELECT id FROM ot_operaciones WHERE ot_id = :ot_id)
        """)
        db.execute(reportes_delete_query, {"ot_id": id})
        
        # Eliminar operaciones asociadas a esta OT
        operaciones_delete_query = text("""
            DELETE FROM ot_operaciones
            WHERE ot_id = :ot_id
        """)
        db.execute(operaciones_delete_query, {"ot_id": id})
        
        # Eliminar la OT
        ot_delete_query = text("""
            DELETE FROM ot
            WHERE id = :id
        """)
        db.execute(ot_delete_query, {"id": id})
        
        db.commit()
        return ot
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_ot(db: Session, id: int, ot_data: Dict[str, Any]) -> Ot:
    """
    Actualiza una OT existente.
    """
    logger.info(f"Actualizando OT con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ot WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        ot_data_copy = ot_data.copy()
        if 'id' in ot_data_copy:
            del ot_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not ot_data_copy:
            return get_ot(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in ot_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa
        query = text(f"""
            UPDATE ot
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_trabajo, INSERTED.area, INSERTED.personal, 
                   INSERTED.tiempo_estimado, INSERTED.titulo, INSERTED.descripcion, 
                   INSERTED.fecha_creacion, INSERTED.fecha_inicio, INSERTED.fecha_fin, 
                   INSERTED.estado, INSERTED.id_deposito
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = ot_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar la OT.")
        
        # Crear el objeto con los datos actualizados
        updated_ot = Ot()
        updated_ot.id = result[0]
        updated_ot.id_trabajo = result[1]
        updated_ot.area = result[2]
        updated_ot.personal = result[3]
        updated_ot.tiempo_estimado = result[4]
        updated_ot.titulo = result[5]
        updated_ot.descripcion = result[6]
        updated_ot.fecha_creacion = result[7]
        updated_ot.fecha_inicio = result[8]
        updated_ot.fecha_fin = result[9]
        updated_ot.estado = result[10]
        updated_ot.id_deposito = result[11]
        
        # Cargar operaciones y reportes
        updated_ot = get_ot(db, id)
        
        return updated_ot
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")

# Verificar estado de OT para finalización
def verificar_estado_ot(db: Session, ot_id: int) -> bool:
    """
    Verifica si todas las operaciones de una OT están finalizadas.
    Retorna True si todas están finalizadas, False en caso contrario.
    """
    try:
        query = text("""
            SELECT COUNT(*) FROM ot_operaciones
            WHERE ot_id = :ot_id AND estado != 'finalizada'
        """)
        
        result = db.execute(query, {"ot_id": ot_id}).scalar()
        
        # Si no hay operaciones pendientes, todas están finalizadas
        return result == 0
    
    except SQLAlchemyError as e:
        logger.error(f"Error al verificar estado de OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al verificar estado: {str(e)}")

def finalizar_ot(db: Session, ot_id: int) -> Ot:
    """
    Finaliza una OT verificando que todas sus operaciones estén completas.
    """
    try:
        # Verificar que la OT existe
        ot = get_ot(db, ot_id)
        if not ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada.")
        
        # Verificar que todas las operaciones están finalizadas
        todas_finalizadas = verificar_estado_ot(db, ot_id)
        if not todas_finalizadas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se puede finalizar la OT porque tiene operaciones pendientes."
            )
        
        # Actualizar el estado de la OT
        ot_data = {
            "estado": "finalizada",
            "fecha_fin": datetime.datetime.now()
        }
        
        # Actualizar la OT
        ot_actualizada = update_ot(db, ot_id, ot_data)
        
        return ot_actualizada
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al finalizar OT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al finalizar OT: {str(e)}")
