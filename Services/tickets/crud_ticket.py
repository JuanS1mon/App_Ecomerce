from sqlalchemy import text, or_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any, List

from ...db.models.config.activityLog import ActivityLog
from ...db.models.config.tickets import Ticket
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def create_ticket(db: Session, ticket: Ticket) -> Ticket:
    """
    Crea un nuevo ticket en la base de datos usando SQLAlchemy ORM.
    """
    try:
        # Inicializar el historial si no existe
        if not ticket.historial:
            historial_inicial = [{
                "fecha": datetime.now().isoformat(),
                "usuario": "Sistema",
                "comentario": "Ticket creado"
            }]
            ticket.historial = json.dumps(historial_inicial)
        
        # Usar el ORM para crear el registro
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        # Convertir el campo historial de JSON a objeto Python para la respuesta
        if ticket.historial and isinstance(ticket.historial, str):
            ticket.historial = json.loads(ticket.historial)
            
        return ticket
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el ticket: {str(e)}")
    
def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    """
    Obtiene un ticket por su ID usando SQL directo.
    """
    try:
        # Opción 1: Usar ORM directamente en lugar de SQL directo
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            return None
        
        # Procesar el historial JSON si existe
        if ticket.historial and isinstance(ticket.historial, str):
            try:
                ticket.historial = json.loads(ticket.historial)
            except:
                ticket.historial = []
        
        return ticket
        
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al obtener el ticket: {str(e)}"
        )
    
def gets_tickets(
    db: Session,
    usuario_id: Optional[int] = None,
    solicitante: Optional[str] = None,
    asignado_a: Optional[str] = None,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    categoria: Optional[str] = None,
    busqueda: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Obtiene tickets con filtros opcionales"""
    logger.info("Iniciando consulta de tickets con filtros")
    try:
        # Evitamos usar ORM directo para mayor control
        query = text("""
            SELECT id, titulo, descripcion, categoria, prioridad, estado, 
                  solicitante, email, telefono, departamento, 
                  fecha_creacion, ultima_actualizacion, historial,
                  asignado_a, tiempo_estimado, tiempo_real, ultima_respuesta
            FROM tickets
            WHERE 1=1
        """)
        
        params = {}
        
        # Construir condiciones de filtro
        conditions = []
        if solicitante:
            conditions.append("solicitante = :solicitante")
            params["solicitante"] = solicitante
            
        if asignado_a:
            conditions.append("asignado_a = :asignado_a")
            params["asignado_a"] = asignado_a
            
        if estado:
            conditions.append("estado = :estado")
            params["estado"] = estado
            
        if prioridad:
            conditions.append("prioridad = :prioridad")
            params["prioridad"] = prioridad
            
        if categoria:
            conditions.append("categoria = :categoria")
            params["categoria"] = categoria
            
        if busqueda:
            conditions.append("(titulo LIKE :busqueda OR descripcion LIKE :busqueda)")
            params["busqueda"] = f"%{busqueda}%"
        
        # Agregar condiciones a la consulta
        if conditions:
            query = text(str(query) + " AND " + " AND ".join(conditions))
        
        # Agregar ordenamiento y paginación
        query = text(str(query) + " ORDER BY fecha_creacion DESC OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY")
        params["skip"] = skip
        params["limit"] = limit
        
        logger.info(f"Ejecutando consulta: {query}")
        logger.info(f"Parámetros: {params}")
        
        result = db.execute(query, params)
        tickets = []
        
        for row in result:
            # Convertir el resultado a un diccionario
            ticket_dict = {}
            for i, column_name in enumerate(result.keys()):
                ticket_dict[column_name] = row[i]
                
            # Procesar campos JSON si es necesario
            if 'historial' in ticket_dict and ticket_dict['historial']:
                try:
                    if isinstance(ticket_dict['historial'], str):
                        ticket_dict['historial'] = json.loads(ticket_dict['historial'])
                except:
                    ticket_dict['historial'] = []
            
            # Crear objeto Ticket
            ticket = Ticket(**ticket_dict)
            tickets.append(ticket)
        
        return tickets
    
    except Exception as e:
        logger.error(f"Error en gets_tickets: {e}")
        # No lanzar excepción, devolver lista vacía para manejar errores con elegancia
        return []

# Función para verificar si un ticket existe
def ticket_exists(db: Session, ticket_id: int) -> Optional[Dict[str, Any]]:
    """
    Verifica si un ticket existe y devuelve sus datos como diccionario
    """
    try:
        query = text("""
            SELECT * FROM tickets WHERE id = :ticket_id
        """)
        result = db.execute(query, {"ticket_id": ticket_id})
        ticket_row = result.fetchone()
        
        if not ticket_row:
            return None
        
        # Convertir a diccionario
        ticket_dict = {}
        columns = result.keys()
        for i, column in enumerate(columns):
            ticket_dict[column] = ticket_row[i]
        
        return ticket_dict
    except Exception as e:
        logger.error(f"Error al verificar existencia de ticket: {e}")
        return None

# Función para procesar el historial de un ticket
def process_ticket_history(historial_actual: Any) -> List[Dict[str, Any]]:
    """
    Procesa el historial de un ticket asegurando que sea una lista válida
    """
    if not historial_actual:
        return []
    
    try:
        if isinstance(historial_actual, str):
            historial_actual = json.loads(historial_actual)
        
        # Validación adicional para asegurar que es una lista
        if not isinstance(historial_actual, list):
            return []
            
        return historial_actual
    except Exception as e:
        logger.warning(f"Error al procesar historial existente: {e}")
        return []

# Función para añadir una respuesta al historial de un ticket
def add_response_to_history(
    db: Session, 
    ticket_id: int, 
    respuesta: str,
    respondido_por: str,
    nuevo_estado: Optional[str] = None,
    asignar_a: Optional[str] = None
) -> bool:
    """
    Añade una respuesta al historial de un ticket y actualiza sus datos
    """
    try:
        # Obtener ticket actual
        ticket = get_ticket(db, ticket_id)
        if not ticket:
            logger.error(f"Ticket {ticket_id} no encontrado")
            return False
        
        # Preparar la respuesta y metadata
        ahora = datetime.now()
        ahora_iso = ahora.isoformat()
        
        # Procesar el historial actual
        historial_actual = ticket.historial if ticket.historial else []
        
        # Asegurar que el historial sea una lista
        if not isinstance(historial_actual, list):
            try:
                if isinstance(historial_actual, str):
                    historial_actual = json.loads(historial_actual)
                else:
                    historial_actual = []
            except:
                historial_actual = []
        
        # Añadir nueva entrada al historial con la respuesta
        nueva_entrada_historial = {
            "fecha": ahora_iso,
            "usuario": respondido_por,
            "comentario": f"Respuesta: {respuesta}"
        }
        
        logger.info(f"Añadiendo nueva entrada al historial: {nueva_entrada_historial}")
        
        historial_actual.append(nueva_entrada_historial)
        
        # Preparar la actualización - Convertir historial a JSON
        update_data = {
            "historial": json.dumps(historial_actual),  # Esta es la línea clave
            "ultima_actualizacion": ahora
        }
        
        # Actualizaciones condicionales
        if nuevo_estado and nuevo_estado.strip():
            update_data["estado"] = nuevo_estado
            # Si es "cerrado", actualizar fecha de cierre
            if nuevo_estado.lower() == "cerrado":
                update_data["fecha_cierre"] = ahora
        
        if asignar_a and asignar_a.strip():
            update_data["asignado_a"] = asignar_a
        
        # Actualizar el campo ultima_respuesta si existe
        try:
            # Verificar si la columna existe
            check_column = text("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tickets' AND COLUMN_NAME = 'ultima_respuesta'
            """)
            result = db.execute(check_column)
            if result.scalar() > 0:
                update_data["ultima_respuesta"] = respuesta[:100] + "..." if len(respuesta) > 100 else respuesta
        except Exception as e:
            logger.warning(f"Error al verificar columna ultima_respuesta: {e}")
        
        # Ejecutar la actualización
        logger.info(f"Datos de actualización: {update_data}")
        
        # Construir y ejecutar la consulta SQL
        update_parts = []
        update_params = {"ticket_id": ticket_id}
        
        for key, value in update_data.items():
            update_parts.append(f"{key} = :{key}")
            update_params[key] = value
            
        update_sql = f"""
            UPDATE tickets 
            SET {', '.join(update_parts)}
            WHERE id = :ticket_id
        """
        
        logger.info(f"SQL: {update_sql}")
        logger.info(f"Params: {update_params}")
        
        db.execute(text(update_sql), update_params)
        db.commit()
        
        logger.info(f"Ticket {ticket_id} actualizado correctamente con nueva respuesta")
        return True
        
    except Exception as e:
        logger.error(f"Error al añadir respuesta al historial: {e}")
        db.rollback()
        return False

# Función para registrar actividad
def register_activity(
    db: Session, 
    user_id: Optional[int], 
    action_text: str, 
    timestamp: datetime
) -> bool:
    """
    Registra una actividad en la tabla activity_log
    """
    try:
        # Verificar si la tabla ActivityLog existe
        table_exists = db.execute(text("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'activity_log'
        """)).scalar() > 0
        
        if not table_exists:
            logger.warning("Tabla activity_log no existe, no se registrará la actividad")
            return False
        
        activity = ActivityLog(
            user_id=user_id,
            action=action_text,
            timestamp=timestamp
        )
        db.add(activity)
        db.commit()
        return True
    except Exception as e:
        logger.warning(f"No se pudo registrar la actividad: {e}")
        return False

def get_ticket_statistics_by_period(
    db: Session,
    from_date: datetime,
    to_date: datetime
) -> Dict[str, Any]:
    """
    Obtiene estadísticas completas de tickets para un período específico
    """
    try:
        # Obtener todos los tickets para el período especificado
        tickets_query = db.query(Ticket).filter(Ticket.fecha_creacion.between(from_date, to_date))
        tickets = tickets_query.all()
        
        # Calcular estadísticas de períodos anteriores para comparación
        previous_from_date = from_date - (to_date - from_date)
        previous_to_date = from_date - timedelta(seconds=1)
        previous_tickets_query = db.query(Ticket).filter(
            Ticket.fecha_creacion.between(previous_from_date, previous_to_date)
        )
        previous_tickets = previous_tickets_query.all()
        
        # Calcular totales actuales
        total_tickets = len(tickets)
        abiertos = len([t for t in tickets if t.estado == 'abierto'])
        proceso = len([t for t in tickets if t.estado == 'en_proceso'])
        cerrados = len([t for t in tickets if t.estado == 'cerrado'])
        
        # Calcular totales del período anterior
        prev_total = len(previous_tickets)
        prev_abiertos = len([t for t in previous_tickets if t.estado == 'abierto'])
        prev_proceso = len([t for t in previous_tickets if t.estado == 'en_proceso'])
        prev_cerrados = len([t for t in previous_tickets if t.estado == 'cerrado'])
        
        # Calcular porcentajes de cambio
        def calc_percent_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100)
        
        # Agrupar tickets por estado para gráfico de pie
        por_estado = [abiertos, proceso, cerrados]
        
        # Agrupar tickets por categoría para gráfico de barras
        categorias = ['hardware', 'software', 'red', 'cuenta', 'otro']
        por_categoria = []
        for cat in categorias:
            count = len([t for t in tickets if t.categoria == cat])
            por_categoria.append(count)
        
        # Agrupar tickets por prioridad para gráfico de donut
        prioridades = ['baja', 'media', 'alta', 'critica']
        por_prioridad = []
        for prio in prioridades:
            count = len([t for t in tickets if t.prioridad == prio])
            por_prioridad.append(count)
        
        # Datos para gráfico de tendencia
        # Para simplificar, dividimos el período en 7 partes iguales
        tendencia_nuevos = []
        tendencia_resueltos = []
        
        delta = (to_date - from_date) / 7
        for i in range(7):
            segment_start = from_date + delta * i
            segment_end = from_date + delta * (i + 1) if i < 6 else to_date
            
            # Tickets nuevos en este segmento
            nuevos = len([t for t in tickets if segment_start <= t.fecha_creacion <= segment_end])
            tendencia_nuevos.append(nuevos)
            
            # Tickets resueltos en este segmento
            resueltos = len([t for t in tickets if 
                           t.estado == 'cerrado' and 
                           t.ultima_actualizacion and
                           segment_start <= t.ultima_actualizacion <= segment_end])
            tendencia_resueltos.append(resueltos)
        
        # Tickets recientes (últimos 5)
        tickets_recientes = db.query(Ticket).order_by(desc(Ticket.fecha_creacion)).limit(5).all()
        recientes_formateados = []
        for t in tickets_recientes:
            recientes_formateados.append({
                "id": t.id,
                "titulo": t.titulo,
                "solicitante": t.solicitante or t.email,
                "estado": t.estado,
                "fecha_creacion": t.fecha_creacion.isoformat() if t.fecha_creacion else None
            })
        
        # Tickets críticos (prioridad crítica y abiertos o en proceso)
        tickets_criticos = db.query(Ticket).filter(
            Ticket.prioridad == 'critica',
            Ticket.estado.in_(['abierto', 'en_proceso'])
        ).order_by(desc(Ticket.fecha_creacion)).limit(5).all()
        
        criticos_formateados = []
        for t in tickets_criticos:
            criticos_formateados.append({
                "id": t.id,
                "titulo": t.titulo,
                "departamento": t.departamento or "No asignado",
                "estado": t.estado,
                "fecha_creacion": t.fecha_creacion.isoformat() if t.fecha_creacion else None
            })
        
        # Métricas de rendimiento
        tiempo_respuesta = 2.5  # valor predeterminado en horas
        
        # Tiempo promedio de resolución (si hay tickets cerrados)
        tiempo_resolucion = 0
        tickets_resueltos = [t for t in tickets if t.estado == 'cerrado' and t.ultima_actualizacion]
        
        if tickets_resueltos:
            tiempo_resolucion = sum(
                (t.ultima_actualizacion - t.fecha_creacion).total_seconds() / 3600 
                for t in tickets_resueltos
            ) / len(tickets_resueltos)
        else:
            tiempo_resolucion = 12.8  # Valor por defecto
        
        # Métricas adicionales
        metricas = {
            "tiempo_primera_respuesta": tiempo_respuesta,
            "tiempo_resolucion": tiempo_resolucion,
            "tasa_resolucion_plazo": 85,  # porcentaje
            "satisfaccion_cliente": 4.5   # de 5
        }
        
        # Construir y devolver el objeto de estadísticas completo
        return {
            "total": total_tickets,
            "abiertos": abiertos,
            "proceso": proceso,
            "cerrados": cerrados,
            "comparacion": {
                "total": calc_percent_change(total_tickets, prev_total),
                "abiertos": calc_percent_change(abiertos, prev_abiertos),
                "proceso": calc_percent_change(proceso, prev_proceso),
                "cerrados": calc_percent_change(cerrados, prev_cerrados)
            },
            "porEstado": por_estado,
            "porCategoria": por_categoria,
            "porPrioridad": por_prioridad,
            "tendencia": {
                "nuevos": tendencia_nuevos,
                "resueltos": tendencia_resueltos
            },
            "ticketsRecientes": recientes_formateados,
            "ticketsCriticos": criticos_formateados,
            "metricas": metricas
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de tickets: {e}")
        return {}
    
def update_ticket(db: Session, ticket_id: int, ticket_data: Dict[str, Any]) -> Ticket:
    logger.info(f"Actualizando Ticket con ID = {ticket_id}")
    logger.info(f"Tipo de ticket_data: {type(ticket_data)}")
    logger.info(f"Contenido de ticket_data: {ticket_data}")

    """
    Actualiza un ticket por su ID usando SQL directo.
    """
    logger.info(f"Actualizando Ticket con ID = {ticket_id}")
    try:
         # Verificar que ticket_data es un diccionario
        if not isinstance(ticket_data, dict):
            logger.error(f"Error: ticket_data debe ser un diccionario, pero es {type(ticket_data)}")
            raise ValueError(f"ticket_data debe ser un diccionario, pero es {type(ticket_data)}")
            
        # Filtrar valores no serializables como objetos datetime
        ticket_data_serializable = {}
        for k, v in ticket_data.items():
            if isinstance(v, datetime):
                ticket_data_serializable[k] = v.isoformat()
            else:
                ticket_data_serializable[k] = v
                
        logger.debug(f"Datos de actualización: {ticket_data_serializable}")
   
        # Primero verificamos que el registro existe
        check_query = text("""
            SELECT * FROM tickets
            WHERE id = :ticket_id
        """)
        
        result = db.execute(check_query, {"ticket_id": ticket_id})
        ticket_actual = result.fetchone()
        
        if not ticket_actual:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        
        ticket_actual_dict = dict(ticket_actual)
        
        # Convertir el historial actual de JSON a Python si existe
        historial_actual = []
        if 'historial' in ticket_actual_dict and ticket_actual_dict['historial']:
            if isinstance(ticket_actual_dict['historial'], str):
                historial_actual = json.loads(ticket_actual_dict['historial'])
            else:
                historial_actual = ticket_actual_dict['historial']
        
        # Preparar datos para actualizar historial si hay cambios relevantes
        cambios = []
        for key, new_value in ticket_data.items():
            if key != 'historial' and key != 'comentario' and key != 'usuario_modificacion' and key in ticket_actual_dict:
                old_value = ticket_actual_dict[key]
                if new_value is not None and new_value != old_value:
                    cambios.append(f"{key}: {old_value} -> {new_value}")
        
        # Si hay cambios o hay un comentario, añadir entrada al historial
        if cambios or 'comentario' in ticket_data:
            entrada = {
                "fecha": datetime.now().isoformat(),
                "usuario": ticket_data.get('usuario_modificacion', 'Sistema'),
                "comentario": ""
            }
            
            if cambios:
                entrada["comentario"] += "Actualización: " + ", ".join(cambios)
            
            if 'comentario' in ticket_data and ticket_data['comentario']:
                if entrada["comentario"]:
                    entrada["comentario"] += "\n"
                entrada["comentario"] += f"Comentario: {ticket_data['comentario']}"
            
            historial_actual.append(entrada)
            ticket_data['historial'] = json.dumps(historial_actual)
        
        # Eliminar campos que no son columnas de la tabla
        ticket_data_copy = ticket_data.copy()
        if 'comentario' in ticket_data_copy:
            del ticket_data_copy['comentario']
        if 'usuario_modificacion' in ticket_data_copy:
            del ticket_data_copy['usuario_modificacion']
        
        # Si hay un cambio de estado a 'cerrado', actualizamos la fecha
        if 'estado' in ticket_data_copy and ticket_data_copy['estado'] == 'cerrado':
            ticket_data_copy['ultima_actualizacion'] = datetime.now()
        
        # Si no hay campos para actualizar, retornar el registro como está
        if not ticket_data_copy:
            # Convertir historial a objeto Python si es string
            if 'historial' in ticket_actual_dict and isinstance(ticket_actual_dict['historial'], str):
                ticket_actual_dict['historial'] = json.loads(ticket_actual_dict['historial'])
            return Ticket(**ticket_actual_dict)
        
        # Construir la consulta de actualización dinámica
        set_clauses = ", ".join([f"{field} = :{field}" for field in ticket_data_copy.keys()])
        update_query = text(f"""
            UPDATE tickets
            SET {set_clauses}
            OUTPUT INSERTED.*
            WHERE id = :ticket_id
        """)
        
        # Agregar el ID al diccionario de parámetros
        params = ticket_data_copy.copy()
        params['ticket_id'] = ticket_id
        
        # Ejecutar la actualización
        result = db.execute(update_query, params)
        updated_record = result.fetchone()
        db.commit()
        
        # Convertir a diccionario y procesar historial
        updated_dict = dict(updated_record)
        if 'historial' in updated_dict and isinstance(updated_dict['historial'], str):
            updated_dict['historial'] = json.loads(updated_dict['historial'])
        
        return Ticket(**updated_dict)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el ticket: {str(e)}")

def delete_ticket(db: Session, ticket_id: int) -> Dict[str, Any]:
    """
    Elimina un ticket por su ID usando SQL directo.
    """
    try:
        # Primero obtenemos el registro para verificar que existe
        get_query = text("""
            SELECT * FROM tickets
            WHERE id = :ticket_id
        """)
        
        result = db.execute(get_query, {"ticket_id": ticket_id})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        
        # Guardar el registro para devolverlo
        ticket_dict = dict(record)
        
        # Si existe, procedemos a eliminarlo
        delete_query = text("""
            DELETE FROM tickets
            WHERE id = :ticket_id
        """)
        
        db.execute(delete_query, {"ticket_id": ticket_id})
        db.commit()
        
        # Convertir historial a objeto Python si es string
        if 'historial' in ticket_dict and isinstance(ticket_dict['historial'], str):
            ticket_dict['historial'] = json.loads(ticket_dict['historial'])
        
        return ticket_dict
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el ticket: {str(e)}")

def get_ticket_statistics(
    db: Session, 
    period: str, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Genera estadísticas de tickets para el dashboard usando SQL directo.
    """
    try:
        # Preparar fechas según el periodo
        today = datetime.now()
        
        if period == "hoy":
            start = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end = today
        elif period == "semana":
            # Inicio de semana (lunes)
            days_to_monday = today.weekday()
            start = (today - datetime.timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = today
        elif period == "mes":
            # Inicio de mes
            start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = today
        else:  # personalizado
            if start_date and end_date:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59)
            else:
                # Por defecto último mes
                start = (today - datetime.timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
                end = today
        
        # SQL para obtener tickets en el periodo actual
        query_periodo = text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'abierto' THEN 1 ELSE 0 END) as abiertos,
                SUM(CASE WHEN estado = 'proceso' THEN 1 ELSE 0 END) as proceso,
                SUM(CASE WHEN estado = 'cerrado' THEN 1 ELSE 0 END) as cerrados
            FROM tickets
            WHERE fecha_creacion BETWEEN :start_date AND :end_date
        """)
        
        result_periodo = db.execute(query_periodo, {
            "start_date": start,
            "end_date": end
        })
        stats_periodo = dict(result_periodo.fetchone())
        
        # Calcular periodo anterior para comparación
        delta = end - start
        start_anterior = start - delta
        end_anterior = start - datetime.timedelta(microseconds=1)
        
        # SQL para obtener tickets en el periodo anterior
        query_anterior = text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'abierto' THEN 1 ELSE 0 END) as abiertos,
                SUM(CASE WHEN estado = 'proceso' THEN 1 ELSE 0 END) as proceso,
                SUM(CASE WHEN estado = 'cerrado' THEN 1 ELSE 0 END) as cerrados
            FROM tickets
            WHERE fecha_creacion BETWEEN :start_date AND :end_date
        """)
        
        result_anterior = db.execute(query_anterior, {
            "start_date": start_anterior,
            "end_date": end_anterior
        })
        stats_anterior = dict(result_anterior.fetchone())
        
        # Calcular porcentajes de cambio
        def calc_porcentaje_cambio(actual, anterior):
            actual = actual or 0
            anterior = anterior or 0
            if anterior == 0:
                return 100 if actual > 0 else 0
            return round(((actual - anterior) / anterior) * 100)
        
        # SQL para obtener distribución por categoría
        query_categoria = text("""
            SELECT categoria, COUNT(*) as count
            FROM tickets
            WHERE fecha_creacion BETWEEN :start_date AND :end_date
            GROUP BY categoria
        """)
        
        result_categoria = db.execute(query_categoria, {
            "start_date": start,
            "end_date": end
        })
        
        # Categorías conocidas (para mantener el orden)
        cats_conocidas = ["Hardware", "Software", "Red/Conectividad", "Cuentas/Accesos", "Otro"]
        por_categoria = [0] * len(cats_conocidas)
        
        for row in result_categoria:
            cat = row['categoria']
            count = row['count']
            if cat in cats_conocidas:
                por_categoria[cats_conocidas.index(cat)] = count
            else:
                # Si es una categoría no conocida, añadirla a "Otro"
                por_categoria[-1] += count
        
        # SQL para obtener distribución por prioridad
        query_prioridad = text("""
            SELECT prioridad, COUNT(*) as count
            FROM tickets
            WHERE fecha_creacion BETWEEN :start_date AND :end_date
            GROUP BY prioridad
        """)
        
        result_prioridad = db.execute(query_prioridad, {
            "start_date": start,
            "end_date": end
        })
        
        prioridades = {"baja": 0, "media": 0, "alta": 0, "critica": 0}
        for row in result_prioridad:
            prioridad = row['prioridad']
            if prioridad in prioridades:
                prioridades[prioridad] = row['count']
        
        por_prioridad = [prioridades["baja"], prioridades["media"], prioridades["alta"], prioridades["critica"]]
        
        # SQL para obtener tickets recientes
        query_recientes = text("""
            SELECT id, titulo, solicitante, estado, fecha_creacion
            FROM tickets
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """)
        
        result_recientes = db.execute(query_recientes)
        tickets_recientes = []
        for row in result_recientes:
            ticket_dict = dict(row)
            ticket_dict['fecha_creacion'] = ticket_dict['fecha_creacion'].isoformat() if ticket_dict['fecha_creacion'] else None
            tickets_recientes.append(ticket_dict)
        
        # SQL para obtener tickets críticos
        query_criticos = text("""
            SELECT id, titulo, departamento, fecha_creacion
            FROM tickets
            WHERE prioridad = 'critica' AND estado != 'cerrado'
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """)
        
        result_criticos = db.execute(query_criticos)
        tickets_criticos = []
        for row in result_criticos:
            ticket_dict = dict(row)
            ticket_dict['fecha_creacion'] = ticket_dict['fecha_creacion'].isoformat() if ticket_dict['fecha_creacion'] else None
            tickets_criticos.append(ticket_dict)
        
        # Generar datos para gráfico de tendencia (simplificado)
        # Para una implementación real, se necesitaría una consulta SQL más compleja
        # Aquí usamos datos ficticios basados en el número de tickets
        total = stats_periodo.get('total') or 0
        nuevos = [5, 8, 4, 3, 2, 5, 1] if total < 50 else [15, 22, 18, 25, 30, 21, 17]
        resueltos = [3, 5, 2, 4, 3, 7, 2] if (stats_periodo.get('cerrados') or 0) < 50 else [12, 18, 15, 22, 28, 19, 15]
        
        # Construir y devolver el resultado
        return {
            "total": stats_periodo.get('total') or 0,
            "abiertos": stats_periodo.get('abiertos') or 0,
            "proceso": stats_periodo.get('proceso') or 0,
            "cerrados": stats_periodo.get('cerrados') or 0,
            "comparacion": {
                "total": calc_porcentaje_cambio(stats_periodo.get('total'), stats_anterior.get('total')),
                "abiertos": calc_porcentaje_cambio(stats_periodo.get('abiertos'), stats_anterior.get('abiertos')),
                "proceso": calc_porcentaje_cambio(stats_periodo.get('proceso'), stats_anterior.get('proceso')),
                "cerrados": calc_porcentaje_cambio(stats_periodo.get('cerrados'), stats_anterior.get('cerrados'))
            },
            "porEstado": [
                stats_periodo.get('abiertos') or 0,
                stats_periodo.get('proceso') or 0,
                stats_periodo.get('cerrados') or 0
            ],
            "porCategoria": por_categoria,
            "tendencia": {
                "nuevos": nuevos,
                "resueltos": resueltos
            },
            "porPrioridad": por_prioridad,
            "ticketsRecientes": tickets_recientes,
            "ticketsCriticos": tickets_criticos
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener estadísticas de tickets: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al generar estadísticas: {str(e)}")