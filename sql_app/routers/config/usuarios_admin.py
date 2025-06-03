"""
Módulo de gestión de usuarios para administradores
Versión simplificada y funcional
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from Services.security.security import get_current_user, require_admin
from db.database import get_db
from db.schemas.config.Usuarios import UserDB

# Configuración
templates = Jinja2Templates(directory="static/html")
logger = logging.getLogger(__name__)

router = APIRouter(
    include_in_schema=False,  
    prefix="/usuarios_admin",
    tags=["Usuarios Admin"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# Modelos de respuesta
class UserResponse(BaseModel):
    id: int
    usuario: str
    nombre: str
    email: str
    activo: bool

class RoleResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    usuarios_count: int = 0

# ==================== RUTAS ESENCIALES ====================

@router.get("/", response_class=HTMLResponse)
async def usuarios_admin_page(
    request: Request,
    current_user: UserDB = Depends(get_current_user)
):
    """Página principal de administración de usuarios"""
    require_admin(current_user)
    return templates.TemplateResponse("config/usuarios_admin.html", {
        "request": request,
        "user": current_user
    })

@router.get("/usuarios/", response_model=List[UserResponse])
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    search: Optional[str] = None,
    activo: Optional[bool] = None
):
    """Lista todos los usuarios con filtros opcionales"""
    require_admin(current_user)
    
    try:
        # Import del modelo
        try:
            from ...db.models.config.usuarios import usuarios as UsuariosModel
        except ImportError:
            from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
        
        query = db.query(UsuariosModel)
        
        # Filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (UsuariosModel.usuario.ilike(search_term)) |
                (UsuariosModel.nombre.ilike(search_term)) |
                (UsuariosModel.email.ilike(search_term))
            )
        
        if activo is not None:
            query = query.filter(UsuariosModel.activo == activo)
        
        usuarios = query.order_by(UsuariosModel.nombre).all()
        
        return [
            UserResponse(
                id=user.id,
                usuario=user.usuario,
                nombre=user.nombre or "",
                email=user.email or "",
                activo=user.activo
            )
            for user in usuarios
        ]
        
    except Exception as e:
        logger.error(f"Error al listar usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/roles/", response_model=List[RoleResponse])
async def listar_roles(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    search: Optional[str] = None
):
    """Lista todos los roles disponibles"""
    require_admin(current_user)
    
    try:
        # Import del modelo
        try:
            from ...db.models.config.roles import roles as RolesModel
        except ImportError:
            from sql_app.db.models.config.roles import roles as RolesModel
        
        query = db.query(RolesModel)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (RolesModel.nombre.ilike(search_term)) |
                (RolesModel.descripcion.ilike(search_term))
            )
        
        roles = query.order_by(RolesModel.nombre).all()
        
        # Contar usuarios por rol (implementación básica)
        roles_response = []
        for rol in roles:
            try:
                # Para simplificar, ponemos contador en 0
                # En una implementación completa, se haría la consulta real
                usuarios_count = 0
                roles_response.append(RoleResponse(
                    id=rol.id,
                    nombre=rol.nombre,
                    descripcion=rol.descripcion or "",
                    usuarios_count=usuarios_count
                ))
            except Exception as e:
                logger.warning(f"Error al contar usuarios para rol {rol.nombre}: {str(e)}")
                roles_response.append(RoleResponse(
                    id=rol.id,
                    nombre=rol.nombre,
                    descripcion=rol.descripcion or "",
                    usuarios_count=0
                ))
        
        return roles_response
        
    except Exception as e:
        logger.error(f"Error al listar roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/roles/tecnico", response_model=List[Dict[str, Any]])
async def obtener_usuarios_tecnico(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Obtiene usuarios con rol técnico - versión simplificada"""
    require_admin(current_user)
    
    try:
        # Datos estáticos para pruebas
        usuarios_tecnico = [
            {
                "id": 1,
                "usuario": "tecnico1",
                "nombre": "Técnico Principal",
                "email": "tecnico1@empresa.com",
                "activo": True
            },
            {
                "id": 2,
                "usuario": "soporte1",
                "nombre": "Soporte Técnico",
                "email": "soporte@empresa.com",
                "activo": True
            }
        ]
        
        return usuarios_tecnico
        
    except Exception as e:
        logger.error(f"Error al obtener usuarios técnicos: {str(e)}")
        return []

@router.get("/mi-perfil", response_model=Dict[str, Any])
async def obtener_mi_perfil(
    current_user: UserDB = Depends(get_current_user)
):
    """Obtiene información del perfil del usuario actual"""
    
    try:
        return {
            "success": True,
            "data": {
                "id": current_user.id,
                "usuario": current_user.usuario,
                "nombre": current_user.nombre,
                "email": current_user.email,
                "activo": current_user.activo,
                "roles": ["usuario"]  # Roles básicos por defecto
            }
        }
        
    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ==================== FUNCIONES ADMINISTRATIVAS ====================

@router.post("/usuarios/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Activa/desactiva un usuario"""
    require_admin(current_user)
    
    try:
        # Import del modelo
        try:
            from ...db.models.config.usuarios import usuarios as UsuariosModel
        except ImportError:
            from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
        
        user = db.query(UsuariosModel).filter(UsuariosModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # No permitir desactivar al propio usuario administrador
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")
        
        user.activo = not user.activo
        db.commit()
        
        return {
            "success": True,
            "message": f"Usuario {'activado' if user.activo else 'desactivado'} correctamente",
            "user_id": user_id,
            "new_status": user.activo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al cambiar estado del usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/usuarios/{user_id}")
async def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Elimina un usuario (solo para administradores)"""
    require_admin(current_user)
    
    try:
        # Import del modelo
        try:
            from ...db.models.config.usuarios import usuarios as UsuariosModel
        except ImportError:
            from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
        
        user = db.query(UsuariosModel).filter(UsuariosModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # No permitir eliminar al propio usuario administrador
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
        
        db.delete(user)
        db.commit()
        
        return {
            "success": True,
            "message": "Usuario eliminado correctamente",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
