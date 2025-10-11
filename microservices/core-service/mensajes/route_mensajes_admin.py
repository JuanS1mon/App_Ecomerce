"""
Router para administración de mensajes
Endpoints específicos para la página de administración
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, date

from ...db.database import get_db
from ...Services.security.security import get_current_user
from Services.mensajes import schema_mensajes
from Services.mensajes.crud_mensajes import CrudMensajes
from db.models.config.usuarios import Usuarios

router = APIRouter(
    prefix="/admin/api/mensajes",
    tags=["admin-mensajes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schema_mensajes.MensajeResponse])
async def listar_mensajes_admin(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tipo: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    leido: Optional[bool] = Query(None),
    busqueda: Optional[str] = Query(None),
    usuario_id: Optional[int] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None)
):
    """
    Obtener lista de mensajes con filtros para administración
    """
    try:
        # Verificar que el usuario sea admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador")
        
        # Aplicar filtros
        filtros = {}
        if tipo:
            filtros['tipo'] = tipo
        if prioridad:
            filtros['prioridad'] = prioridad
        if leido is not None:
            filtros['leido'] = leido
        if usuario_id:
            filtros['usuario_id'] = usuario_id
        if fecha_desde:
            filtros['fecha_desde'] = fecha_desde
        if fecha_hasta:
            filtros['fecha_hasta'] = fecha_hasta
        if busqueda:
            filtros['busqueda'] = busqueda
        
        mensajes = CrudMensajes.get_mensajes_filtrados(
            db=db, 
            filtros=filtros,
            skip=skip, 
            limit=limit
        )
        
        return mensajes
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener mensajes: {str(e)}")

@router.get("/estadisticas")
async def obtener_estadisticas_mensajes(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Obtener estadísticas de mensajes para el dashboard
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        stats = CrudMensajes.get_estadisticas_mensajes(db=db)
        
        return {
            "total": stats.get("total", 0),
            "no_leidos": stats.get("no_leidos", 0),
            "urgentes": stats.get("urgentes", 0),
            "hoy": stats.get("hoy", 0),
            "por_tipo": stats.get("por_tipo", {}),
            "por_prioridad": stats.get("por_prioridad", {}),
            "tendencia_semanal": stats.get("tendencia_semanal", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.post("/", response_model=schema_mensajes.MensajeResponse)
async def crear_mensaje_admin(
    mensaje: schema_mensajes.MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Crear un nuevo mensaje desde la administración
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Validar que el usuario receptor existe
        if not CrudMensajes.verificar_usuario_existe(db=db, usuario_id=mensaje.usuario_id):
            raise HTTPException(status_code=404, detail="Usuario receptor no encontrado")
        
        # Validar metadatos JSON si se proporcionan
        if mensaje.metadatos:
            try:
                if isinstance(mensaje.metadatos, str):
                    json.loads(mensaje.metadatos)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Metadatos deben ser JSON válido")
        
        # Agregar metadatos de origen
        metadatos_origen = {
            "origen": "admin",
            "creado_por": current_user.codigo,  # Usar codigo como en route_mensajes.py
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if mensaje.metadatos:
            if isinstance(mensaje.metadatos, str):
                metadatos_existentes = json.loads(mensaje.metadatos)
            else:
                metadatos_existentes = mensaje.metadatos
            metadatos_origen.update(metadatos_existentes)
        
        mensaje.metadatos = metadatos_origen
        
        db_mensaje = CrudMensajes.create_mensaje(db=db, mensaje=mensaje)
        return db_mensaje
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear mensaje: {str(e)}")

@router.get("/{mensaje_id}", response_model=schema_mensajes.MensajeResponse)
async def obtener_mensaje_admin(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Obtener un mensaje específico por ID
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        mensaje = CrudMensajes.get_mensaje_by_id(db=db, mensaje_id=mensaje_id)
        if not mensaje:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        return mensaje
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener mensaje: {str(e)}")

@router.put("/{mensaje_id}", response_model=schema_mensajes.MensajeResponse)
async def actualizar_mensaje_admin(
    mensaje_id: int,
    mensaje_update: schema_mensajes.MensajeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Actualizar un mensaje existente
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Verificar que el mensaje existe
        mensaje_existente = CrudMensajes.get_mensaje_by_id(db=db, mensaje_id=mensaje_id)
        if not mensaje_existente:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        # Si se cambia el usuario, verificar que existe
        if mensaje_update.usuario_id and mensaje_update.usuario_id != mensaje_existente.usuario_id:
            if not CrudMensajes.verificar_usuario_existe(db=db, usuario_id=mensaje_update.usuario_id):
                raise HTTPException(status_code=404, detail="Usuario receptor no encontrado")
        
        # Validar metadatos JSON si se proporcionan
        if mensaje_update.metadatos:
            try:
                if isinstance(mensaje_update.metadatos, str):
                    json.loads(mensaje_update.metadatos)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Metadatos deben ser JSON válido")
        
        # Agregar metadatos de modificación
        if mensaje_update.metadatos:
            if isinstance(mensaje_update.metadatos, str):
                metadatos = json.loads(mensaje_update.metadatos)
            else:
                metadatos = mensaje_update.metadatos
        else:
            metadatos = mensaje_existente.metadatos or {}
        
        metadatos.update({
            "modificado_por": current_user.codigo,  # Usar codigo como en route_mensajes.py
            "fecha_modificacion": datetime.utcnow().isoformat()
        })
        
        mensaje_update.metadatos = metadatos
        
        mensaje_actualizado = CrudMensajes.update_mensaje(db=db, mensaje_id=mensaje_id, mensaje_update=mensaje_update)
        return mensaje_actualizado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar mensaje: {str(e)}")

@router.patch("/{mensaje_id}/leido")
async def toggle_mensaje_leido_admin(
    mensaje_id: int,
    leido: bool,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Cambiar el estado de lectura de un mensaje
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        resultado = CrudMensajes.marcar_mensaje_leido(db=db, mensaje_id=mensaje_id, leido=leido)
        if not resultado:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        return {
            "mensaje": f"Mensaje marcado como {'leído' if leido else 'no leído'}",
            "mensaje_id": mensaje_id,
            "leido": leido,
            "fecha_actualizacion": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado: {str(e)}")

@router.delete("/{mensaje_id}")
async def eliminar_mensaje_admin(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Eliminar un mensaje
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        resultado = CrudMensajes.delete_mensaje(db=db, mensaje_id=mensaje_id)
        if not resultado:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        return {
            "mensaje": "Mensaje eliminado correctamente",
            "mensaje_id": mensaje_id,
            "fecha_eliminacion": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar mensaje: {str(e)}")

@router.get("/usuarios/lista")
async def listar_usuarios_para_mensajes(
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Obtener lista de usuarios para el selector de destinatarios
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        usuarios = CrudMensajes.get_usuarios_activos(db=db)
        
        return [
            {
                "id": usuario.id,
                "nombre": usuario.username,
                "email": usuario.email,
                "es_admin": usuario.is_admin
            }
            for usuario in usuarios
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

@router.post("/lote/marcar-leidos")
async def marcar_lote_leidos(
    mensaje_ids: List[int],
    leido: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Marcar múltiples mensajes como leídos/no leídos
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        resultados = []
        for mensaje_id in mensaje_ids:
            resultado = CrudMensajes.marcar_mensaje_leido(db=db, mensaje_id=mensaje_id, leido=leido)
            resultados.append({
                "mensaje_id": mensaje_id,
                "actualizado": resultado is not None
            })
        
        actualizados = sum(1 for r in resultados if r["actualizado"])
        
        return {
            "mensaje": f"{actualizados} mensajes actualizados",
            "total_solicitados": len(mensaje_ids),
            "actualizados": actualizados,
            "resultados": resultados
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar mensajes en lote: {str(e)}")

@router.delete("/lote/eliminar")
async def eliminar_lote_mensajes(
    mensaje_ids: List[int],
    db: Session = Depends(get_db),
    current_user: Usuarios = Depends(get_current_user)
):
    """
    Eliminar múltiples mensajes
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        resultados = []
        for mensaje_id in mensaje_ids:
            resultado = CrudMensajes.delete_mensaje(db=db, mensaje_id=mensaje_id)
            resultados.append({
                "mensaje_id": mensaje_id,
                "eliminado": resultado is not None
            })
        
        eliminados = sum(1 for r in resultados if r["eliminado"])
        
        return {
            "mensaje": f"{eliminados} mensajes eliminados",
            "total_solicitados": len(mensaje_ids),
            "eliminados": eliminados,
            "resultados": resultados
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar mensajes en lote: {str(e)}")

@router.get("/test/admin")
async def test_admin_endpoint():
    """
    Endpoint de prueba para verificar que el router funciona
    """
    return {
        "mensaje": "Router de administración de mensajes funcionando",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints_disponibles": [
            "GET /admin/api/mensajes/ - Listar mensajes con filtros",
            "GET /admin/api/mensajes/estadisticas - Estadísticas",
            "POST /admin/api/mensajes/ - Crear mensaje",
            "GET /admin/api/mensajes/{id} - Obtener mensaje",
            "PUT /admin/api/mensajes/{id} - Actualizar mensaje",
            "PATCH /admin/api/mensajes/{id}/leido - Toggle leído",
            "DELETE /admin/api/mensajes/{id} - Eliminar mensaje",
            "GET /admin/api/mensajes/usuarios/lista - Listar usuarios",
            "POST /admin/api/mensajes/lote/marcar-leidos - Marcar lote",
            "DELETE /admin/api/mensajes/lote/eliminar - Eliminar lote"
        ]
    }
