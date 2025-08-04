from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.database import get_db
from ...Services.security.security import get_current_user
from ...db.models.config.usuarios import Usuarios
from .schema_mensajes import (
    MensajeCreate, MensajeUpdate, MensajeResponse, 
    MensajeResumen, EstadisticasMensajes
)
from .crud_mensajes import CrudMensajes

router = APIRouter(prefix="/api/mensajes", tags=["mensajes"])

@router.get("/navbar", response_model=List[MensajeResumen])
async def obtener_mensajes_navbar(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Obtener mensajes recientes para mostrar en la navbar"""
    return CrudMensajes.obtener_mensajes_recientes_navbar(db, current_user.codigo)

@router.get("/no-leidos/count")
async def contar_mensajes_no_leidos(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Contar mensajes no leídos del usuario actual"""
    count = CrudMensajes.contar_mensajes_no_leidos(db, current_user.codigo)
    return {"count": count}

@router.get("/", response_model=List[MensajeResponse])
async def obtener_mis_mensajes(
    solo_no_leidos: bool = False,
    limite: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Obtener mensajes del usuario actual"""
    return CrudMensajes.obtener_mensajes_usuario(
        db, current_user.codigo, solo_no_leidos, limite, offset
    )

@router.get("/estadisticas", response_model=EstadisticasMensajes)
async def obtener_estadisticas_mensajes(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Obtener estadísticas de mensajes del usuario actual"""
    return CrudMensajes.obtener_estadisticas(db, current_user.codigo)

@router.get("/{mensaje_id}", response_model=MensajeResponse)
async def obtener_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Obtener un mensaje específico"""
    mensaje = CrudMensajes.obtener_mensaje(db, mensaje_id)
    if not mensaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    
    # Verificar que el usuario actual es el receptor del mensaje
    if mensaje.usuario_receptor_id != current_user.codigo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este mensaje"
        )
    
    return mensaje

@router.post("/", response_model=MensajeResponse)
async def crear_mensaje(
    mensaje: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Crear un nuevo mensaje"""
    # Si no se especifica emisor, usar el usuario actual
    if mensaje.usuario_emisor_id is None:
        mensaje.usuario_emisor_id = current_user.codigo
    
    # Verificar que el emisor es el usuario actual (salvo admin que puede enviar como sistema)
    if mensaje.usuario_emisor_id != current_user.codigo and mensaje.usuario_emisor_id is not None:
        # TODO: Verificar si el usuario tiene permisos de admin para enviar como sistema
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes enviar mensajes en nombre de otros usuarios"
        )
    
    db_mensaje = CrudMensajes.crear_mensaje(db, mensaje)
    
    # Convertir a response con información adicional
    mensajes = CrudMensajes.obtener_mensajes_usuario(db, db_mensaje.usuario_receptor_id, limite=1)
    if mensajes:
        return mensajes[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el mensaje"
        )

@router.patch("/{mensaje_id}/leido")
async def marcar_como_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Marcar un mensaje como leído"""
    success = CrudMensajes.marcar_como_leido(db, mensaje_id, current_user.codigo)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado o ya leído"
        )
    return {"message": "Mensaje marcado como leído"}

@router.patch("/todos/leido")
async def marcar_todos_como_leidos(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Marcar todos los mensajes como leídos"""
    try:
        count = CrudMensajes.marcar_todos_como_leidos(db, current_user.codigo)
        return {"message": f"{count} mensajes marcados como leídos"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar mensajes como leídos: {str(e)}"
        )

@router.patch("/test/todos/leido")
async def test_marcar_todos_como_leidos():
    """Endpoint de prueba sin autenticación para testing"""
    return {
        "message": "3 mensajes marcados como leídos (modo test)",
        "success": True,
        "note": "Este es un endpoint de prueba sin persistencia"
    }

@router.delete("/{mensaje_id}")
async def eliminar_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Eliminar un mensaje"""
    success = CrudMensajes.eliminar_mensaje(db, mensaje_id, current_user.codigo)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    return {"message": "Mensaje eliminado"}

# Rutas administrativas (requieren permisos especiales)
@router.post("/sistema", response_model=MensajeResponse)
async def crear_mensaje_sistema(
    mensaje: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """Crear un mensaje del sistema (solo administradores)"""
    # TODO: Verificar permisos de administrador
    # Por ahora, permitir que cualquier usuario envíe mensajes del sistema
    
    mensaje.usuario_emisor_id = None  # Mensaje del sistema
    db_mensaje = CrudMensajes.crear_mensaje(db, mensaje)
    
    # Convertir a response con información adicional
    mensajes = CrudMensajes.obtener_mensajes_usuario(db, db_mensaje.usuario_receptor_id, limite=1)
    if mensajes:
        return mensajes[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el mensaje del sistema"
        )
