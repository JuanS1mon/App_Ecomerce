from fastapi import APIRouter, HTTPException, status, Depends, Query, Form, UploadFile, File, Request
from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.config.activityLog import ActivityLog
from .schema_ticket import TicketCreate, TicketUpdate, TicketRead
from .model_ticket import Ticket 
from .crud_ticket import add_response_to_history, create_ticket, get_ticket, get_ticket_statistics_by_period, gets_tickets, delete_ticket, register_activity, update_ticket
from Services.security.security import get_current_user
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from typing import Any, Dict, List, Optional
import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# Ruta base para archivos estáticos HTML

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Obtiene la raíz del proyecto
HTML_BASE_PATH = BASE_DIR / "static" / "html" / "ticket"

# ----- Rutas para las páginas HTML -----

@router.get("/nuevo", response_class=HTMLResponse)
async def get_pagina_ticket():
    """Devuelve la página para crear un nuevo ticket"""
    try:
        file_path = HTML_BASE_PATH / "ticket.html"
        logger.info(f"Intentando leer archivo: {file_path}")
        
        if not file_path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Archivo HTML no encontrado: {file_path}"
            )
            
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de creación de ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la página HTML: {str(e)}")

@router.get("/crear", response_class=HTMLResponse)
async def get_pagina_crear_ticket():
    """Alias para la página de creación de tickets (para mayor compatibilidad con enlaces)"""
    return await get_pagina_ticket()

@router.get("/listar", response_class=HTMLResponse)
async def get_pagina_listar_tickets():
    """Devuelve la página para listar todos los tickets"""
    try:
        file_path = HTML_BASE_PATH / "ticket_listar.html"
        logger.info(f"Intentando leer archivo: {file_path}")
        
        if not file_path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Archivo HTML no encontrado: {file_path}"
            )
            
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de listado de tickets: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la página HTML: {str(e)}")

@router.get("/admin", response_class=HTMLResponse)
async def get_pagina_admin_tickets():
    """Devuelve la página de administración de tickets"""
    try:
        file_path = HTML_BASE_PATH / "ticket_admin.html"
        logger.info(f"Intentando leer archivo: {file_path}")
        
        if not file_path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Archivo HTML no encontrado: {file_path}"
            )
            
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de administración de tickets: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la página HTML: {str(e)}")

@router.get("/gestion", response_class=HTMLResponse)
async def get_pagina_gestion_tickets():
    """Devuelve la página para gestionar tickets (responder y cambiar estados)"""
    try:
        file_path = HTML_BASE_PATH / "ticket_gestion.html"
        logger.info(f"Intentando leer archivo: {file_path}")
        
        if not file_path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Archivo HTML no encontrado: {file_path}"
            )
            
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de gestión de tickets: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la página HTML: {str(e)}")
    

@router.post("/responder/{ticket_id}", status_code=status.HTTP_200_OK)
async def responder_ticket(
    ticket_id: int,
    respuesta: str = Form(...),
    nuevo_estado: Optional[str] = Form(None),
    asignar_a: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Procesa una respuesta a un ticket y/o actualización de estado.
    """
    try:
        # Paso 1: Determinar quién responde
        respondido_por = "Sistema"
        if isinstance(current_user, dict):
            respondido_por = current_user.get("nombre") or current_user.get("usuario", "Personal de soporte")
        else:
            respondido_por = getattr(current_user, "nombre", None) or getattr(current_user, "usuario", "Personal de soporte")
        
        # Paso 2: Añadir la respuesta al historial del ticket
        success = add_response_to_history(
            db=db, 
            ticket_id=ticket_id,
            respuesta=respuesta,
            respondido_por=respondido_por,
            nuevo_estado=nuevo_estado,
            asignar_a=asignar_a
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo procesar la respuesta. El ticket podría no existir."
            )
        
        # Paso 3: Registrar la actividad
        user_id = None
        if isinstance(current_user, dict):
            user_id = current_user.get("id")
        else:
            user_id = getattr(current_user, "codigo", None)
            
        action_text = f"Respondió al ticket #{ticket_id}"
        if nuevo_estado:
            action_text += f" y cambió su estado a '{nuevo_estado}'"
            
        register_activity(
            db=db,
            user_id=user_id,
            action_text=action_text,
            timestamp=datetime.now()
        )
        
        # Paso 4: Retornar respuesta de éxito
        return {"success": True, "message": "Respuesta registrada correctamente"}
    
    except HTTPException as e:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        # Manejar cualquier otra excepción
        logger.error(f"Error no manejado al responder al ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la respuesta: {str(e)}"
        )

# ----- API endpoints para procesamiento de formularios 
@router.post("/crear", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def crear_ticket_desde_formulario(
    request: Request,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...),
    prioridad: str = Form(...),
    email: str = Form(...),
    telefono: Optional[str] = Form(None),
    notificaciones: bool = Form(False),
    adjuntos: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- Añadir esta dependencia
):
    """Procesa el formulario de creación de ticket desde la interfaz web"""
    logger.info("Procesando formulario de creación de ticket")
    try:
        # Determinar el solicitante según el tipo de current_user
        solicitante = None
        if isinstance(current_user, dict):
            # Si es un diccionario (JWT)
            solicitante = current_user.get("nombre") or current_user.get("usuario", "Usuario no identificado")
            # También podrías usar current_user["id"] para el ID si lo necesitas
        else:
            # Si es un objeto UserDB
            solicitante = getattr(current_user, "nombre", None) or getattr(current_user, "usuario", "Usuario no identificado")
            # También podrías usar current_user.codigo para el ID si lo necesitas
        
        logger.info(f"Solicitante del ticket: {solicitante}")
        
        # Crear un nuevo objeto Ticket con el solicitante
        nuevo_ticket = Ticket(
            titulo=titulo,
            descripcion=descripcion,
            categoria=categoria,
            prioridad=prioridad,
            estado="abierto",  # Por defecto
            email=email,
            telefono=telefono,
            fecha_creacion=datetime.now(),
            solicitante=solicitante,  # Añadir solicitante
            # Si tienes una relación con la tabla de usuarios, añadir también:
            #usuario_id=current_user.codigo if hasattr(current_user, "codigo") else None
        )
        
        # Llamar a la función create_ticket
        db_ticket = create_ticket(db=db, ticket=nuevo_ticket)
        
        # Registrar la actividad (como haces en Admin.py)
        activity = ActivityLog(
            user_id=getattr(current_user, "codigo", None) if not isinstance(current_user, dict) else current_user.get("id"),
            action=f"Creó un ticket: {titulo}",
            timestamp=datetime.now()
        )
        db.add(activity)
        db.commit()
        
        # Devolver el ticket creado
        return db_ticket
    except Exception as e:
        logger.error(f"Error al procesar formulario de ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el formulario: {str(e)}"
        )
    

# ----- API endpoints para base de datos -----
@router.get("/detalles/{ticket_id}", response_model=Dict[str, Any])
async def get_ticket_details(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    API para obtener detalles completos de un ticket específico, incluyendo su historial
    """
    try:
        logger.info(f"Obteniendo detalles completos del ticket {ticket_id}")
        
        # Obtener el ticket usando la función de crud_ticket.py
        ticket = get_ticket(db, ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )
            
        # Convertir el ticket a diccionario y procesar fechas
        ticket_dict = {}
        for column in ticket.__table__.columns.keys():
            value = getattr(ticket, column)
            
            # Convertir fechas a formato ISO
            if isinstance(value, datetime):
                value = value.isoformat()
                
            ticket_dict[column] = value
        
        # Asegurar que el historial sea una lista correctamente formateada
        if 'historial' in ticket_dict and ticket_dict['historial']:
            # El historial ya debería ser un objeto y no un string,
            # debido a que get_ticket ya procesa el JSON
            logger.info(f"Historial del ticket: {ticket_dict['historial']}")
            
            # Verificación adicional en caso de que sea string
            if isinstance(ticket_dict['historial'], str):
                try:
                    ticket_dict['historial'] = json.loads(ticket_dict['historial'])
                except json.JSONDecodeError:
                    logger.warning(f"Error al decodificar historial para ticket {ticket_id}")
                    ticket_dict['historial'] = []
        else:
            ticket_dict['historial'] = []
            
        logger.info(f"Devolviendo ticket con historial de {len(ticket_dict['historial'])} entradas")
        
        return ticket_dict
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalles del ticket: {str(e)}"
        )


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def routes_post_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """Crea un nuevo ticket"""
    if ticket.titulo is None or ticket.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El título y la descripción son obligatorios")
    try:
        ticket_model = Ticket(**ticket.model_dump())
        db_ticket = create_ticket(db=db, ticket=ticket_model)
        return TicketRead.model_validate(db_ticket)
    except Exception as e:
        logger.error(f"Error al crear ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el ticket.")

@router.get("/id/{id}", response_model=TicketRead)
async def routes_get_ticket_id(id: int, db: Session = Depends(get_db)):
    """Obtiene un ticket por su ID"""
    try:
        db_ticket = get_ticket(db, id)
        if not db_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
        return TicketRead.model_validate(db_ticket)
    except Exception as e:
        logger.error(f"Error al obtener ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el ticket.")
    
@router.get("/gets_tickets", response_model=List[TicketRead])
async def routes_gets_tickets(
    usuario_id: Optional[int] = Query(None),  # Mantenemos para compatibilidad
    solicitante: Optional[str] = Query(None),  # Nuevo parámetro
    asignado_a: Optional[str] = Query(None),   # Nuevo parámetro
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    busqueda: Optional[str] = Query(None),
    solo_mis_tickets: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtiene lista de tickets con filtros opcionales"""
    print("========== DEBUGGING ROUTE /tickets/gets_tickets ==========")
    print(f"Request received at: {datetime.now()}")
    
    try:
        # Determinar el ID del usuario y nombre para filtrado
        user_id = None
        user_name = None
        
        if current_user:
            if isinstance(current_user, dict):
                user_id = current_user.get("id") or current_user.get("codigo")
                user_name = current_user.get("nombre") or current_user.get("usuario")
            else:
                user_id = getattr(current_user, "codigo", None)
                user_name = getattr(current_user, "nombre", None) or getattr(current_user, "usuario", None)
            
            logger.info(f"Usuario actual: ID={user_id}, Nombre={user_name}")
        
        # Si se solicita filtrar por mis tickets y hay usuario autenticado
        nombre_solicitante = None
        nombre_asignado = None
        
        if solo_mis_tickets and user_name:
            # Preparar filtros para "mis tickets" (solicitante o asignado_a)
            nombre_solicitante = user_name
            nombre_asignado = user_name
            logger.info(f"Filtrando solo tickets donde {user_name} es solicitante o está asignado")
        else:
            # Si no es "solo mis tickets", usar los filtros que vinieron en la URL
            nombre_solicitante = solicitante
            nombre_asignado = asignado_a
        
        logger.info(f"Obteniendo tickets con filtros: solicitante={nombre_solicitante}, asignado_a={nombre_asignado}, estado={estado}, prioridad={prioridad}, categoria={categoria}")
        
        # Intentar obtener tickets con los filtros adecuados
        tickets = []
        try:
            # En lugar de usar usuario_id, ahora usamos los campos correctos
            if solo_mis_tickets:
                # Si es "solo mis tickets", hacemos dos consultas y combinamos resultados
                tickets_solicitante = gets_tickets(
                    db, 
                    solicitante=user_name,
                    estado=estado, 
                    prioridad=prioridad,
                    categoria=categoria,
                    busqueda=busqueda,
                    skip=skip, 
                    limit=limit
                ) or []
                
                tickets_asignado = gets_tickets(
                    db, 
                    asignado_a=user_name,
                    estado=estado, 
                    prioridad=prioridad,
                    categoria=categoria,
                    busqueda=busqueda,
                    skip=skip, 
                    limit=limit
                ) or []
                
                # Combinar resultados, eliminando duplicados
                ticket_ids = set()
                tickets = []
                
                for ticket in tickets_solicitante:
                    if ticket.id not in ticket_ids:
                        tickets.append(ticket)
                        ticket_ids.add(ticket.id)
                
                for ticket in tickets_asignado:
                    if ticket.id not in ticket_ids:
                        tickets.append(ticket)
                        ticket_ids.add(ticket.id)
                
                # Re-ordenar por fecha de creación
                tickets.sort(key=lambda x: x.fecha_creacion if x.fecha_creacion else datetime.min, reverse=True)
                
                # Aplicar límite después de combinar
                tickets = tickets[:limit]
                
                logger.info(f"Filtrado combinado (solicitante + asignado): {len(tickets)} tickets")
            else:
                # Si no es "solo mis tickets", usar filtros normales
                tickets = gets_tickets(
                    db, 
                    solicitante=nombre_solicitante,  # Usar el nombre en lugar de ID
                    asignado_a=nombre_asignado,
                    estado=estado, 
                    prioridad=prioridad,
                    categoria=categoria,
                    busqueda=busqueda,
                    skip=skip, 
                    limit=limit
                ) or []
            
            logger.info(f"Se encontraron {len(tickets)} tickets")
            
        except Exception as e:
            logger.error(f"Error al obtener tickets: {str(e)}")
            # En caso de error crítico, devolver lista vacía en lugar de error
        result = []
        for t in tickets:
            try:
                result.append(TicketRead.model_validate(t))
            except Exception as e:
                logger.error(f"Error al convertir ticket a esquema: {str(e)}")
                # Ignoramos este ticket y continuamos
        
        return result
        
    except Exception as e:
        logger.error(f"Error general al obtener tickets: {str(e)}")
        # En caso de error crítico, devolver lista vacía en lugar de error
        return []


@router.put("/id/{id}", response_model=TicketRead)
async def routes_update_ticket(id: int, ticket: TicketUpdate, db: Session = Depends(get_db)):
    """Actualiza un ticket existente"""
    logger.info(f"Actualizando ticket con ID = {id}")
    try:
        ticket_data = ticket.model_dump()
        db_ticket = update_ticket(db=db, id=id, ticket_data=ticket_data)
        if not db_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
        return TicketRead.model_validate(db_ticket)
    except Exception as e:
        logger.error(f"Error al actualizar ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el ticket.")

@router.delete("/id/{id}", response_model=TicketRead)
async def routes_delete_ticket_id(id: int, db: Session = Depends(get_db)):
    """Elimina un ticket por su ID"""
    try:
        db_ticket = get_ticket(db, id)
        if not db_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
        db_ticket = delete_ticket(db, id)
        return TicketRead.model_validate(db_ticket)
    except Exception as e:
        logger.error(f"Error al eliminar ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el ticket.")


@router.get("/detalle/{id}", response_class=HTMLResponse)
async def get_pagina_detalle_ticket(id: int):
    """Devuelve la página de detalle de un ticket específico"""
    try:
        file_path = HTML_BASE_PATH / "ticket_detalle.html"
        logger.info(f"Intentando leer archivo: {file_path}")
        
        if not file_path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Archivo HTML no encontrado: {file_path}"
            )
            
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de detalle de ticket: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la página HTML: {str(e)}")


# ----- API endpoints para estadísticas del dashboard -----
@router.get("/statistics")
async def get_ticket_statistics(
    period: str = Query("semana", description="Período: hoy, semana, mes, trimestre, anio o personalizado"),
    start_date: Optional[str] = Query(None, description="Fecha inicio para período personalizado"),
    end_date: Optional[str] = Query(None, description="Fecha fin para período personalizado"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas de tickets para el panel de administración.
    Si el período es 'personalizado', se deben proporcionar start_date y end_date.
    """
    try:
        # Determinar fechas según el período
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if period == "hoy":
            from_date = today
            to_date = datetime.now()
        elif period == "semana":
            from_date = today - timedelta(days=7)
            to_date = datetime.now()
        elif period == "mes":
            from_date = today - timedelta(days=30)
            to_date = datetime.now()
        elif period == "trimestre":
            from_date = today - timedelta(days=90)
            to_date = datetime.now()
        elif period == "anio":
            from_date = today - timedelta(days=365)
            to_date = datetime.now()
        elif period == "personalizado" and start_date and end_date:
            try:
                from_date = datetime.strptime(start_date, "%Y-%m-%d")
                to_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Formato de fecha inválido. Usar YYYY-MM-DD."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Período no válido o fechas faltantes para período personalizado."
            )
        
        # Obtener estadísticas usando la función del crud
        stats_data = get_ticket_statistics_by_period(db, from_date, to_date)
        
        # Construir respuesta final añadiendo información del período
        response = {
            "period": period,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            **stats_data  # Incluir todos los datos de estadísticas
        }
        
        return response
        
    except HTTPException as e:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de tickets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas de tickets: {str(e)}"
        )

# Ruta para obtener todos los tickets con filtros
@router.get("/gets_tickets", response_model=List[TicketRead]) 
async def get_all_tickets(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    categoria: Optional[str] = None,
    busqueda: Optional[str] = None,
    solo_mis_tickets: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todos los tickets, con opciones de filtrado.
    Si solo_mis_tickets=True, solo devuelve tickets del usuario actual.
    """
    try:
        usuario_id = None
        if solo_mis_tickets:
            usuario_id = current_user.get("id")
        
        tickets = gets_tickets(
            db, 
            usuario_id=usuario_id,
            estado=estado, 
            prioridad=prioridad,
            categoria=categoria,
            busqueda=busqueda,
            skip=skip, 
            limit=limit
        )
        
        logger.info(f"Se encontraron {len(tickets)} tickets con los filtros aplicados")
        return [TicketRead.model_validate(t) for t in tickets]
        
    except Exception as e:
        logger.error(f"Error al obtener tickets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tickets: {str(e)}"
        )