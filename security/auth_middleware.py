"""
Middleware de Autenticación para Rutas Protegidas
================================================

Este middleware maneja la autenticación puramente desde el backend:
1. Verifica tokens JWT antes de servir páginas HTML
2. Redirige automáticamente a login si no hay autenticación válida
3. Inyecta datos del usuario directamente en las plantillas
4. Sistema reutilizable para cualquier ruta que requiera autenticación

Uso:
    from Services.security.auth_middleware import require_auth_for_template
    
    @router.get("/admin")
    async def admin_page(request: Request, user_data: dict = Depends(require_auth_for_template)):
        return templates.TemplateResponse("admin.html", {
            "request": request,
            **user_data  # Incluye user, user_count, activities, etc.
        })
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from db.models.config.usuarios import Usuarios
from db.models.config.roles import Roles, usuario_roles
from db.schemas.config.Usuarios import UserDB
from security.jwt_auth import verify_token, JWTAuthError

# Configurar logger
logger = logging.getLogger("auth_middleware")

# Configuración
LOGIN_PAGE_URL = "/loginpage"
security = HTTPBearer(auto_error=False)

class AuthenticationError(Exception):
    """Excepción para errores de autenticación en middleware"""
    pass

def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extrae el token JWT de la petición.
    PRIORIDAD: Query params > Authorization header > cookies
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Token JWT si se encuentra, None si no
    """
    logger.debug(f"Extracting token from request to: {request.url.path}")
    
    # 1. PRIORIDAD ALTA: Intentar desde query params (para navegadores que no manejan cookies)
    token = request.query_params.get("token")
    if token:
        logger.debug("Token encontrado en query params")
        return token
    
    # 2. Intentar desde Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        logger.debug("Token encontrado en Authorization header")
        return token
    
    # 3. Intentar desde cookies (fallback)
    token = request.cookies.get("access_token")
    if token:
        logger.debug("Token encontrado en cookies")
        return token

    logger.debug("No se encontró token en la petición")
    return None

def get_user_from_token(token: str, db: Session) -> UserDB:
    """
    Obtiene el usuario desde un token JWT validado
    
    Args:
        token: Token JWT
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        AuthenticationError: Si el token es inválido o el usuario no existe
    """
    try:
        # Verificar token
        token_data = verify_token(token)
        
        # Buscar usuario
        user = db.query(Usuarios).filter(
            Usuarios.usuario == token_data.username
        ).first()
        
        if not user:
            raise AuthenticationError(f"Usuario no encontrado: {token_data.username}")
        
        if not user.activo:
            raise AuthenticationError(f"Usuario inactivo: {token_data.username}")
          # Cargar roles - con manejo de errores para compatibilidad
        try:
            roles_query = db.query(Roles.nombre).join(
                usuario_roles, 
                usuario_roles.c.rol_id == Roles.id
            ).filter(
                usuario_roles.c.usuario_id == user.codigo
            ).all()
            
            user.roles = [role[0].lower() for role in roles_query]
            
            # Si no tiene roles asignados, usar rol por defecto basado en el usuario
            if not user.roles:
                if user.usuario.lower() in ['admin', 'administrador']:
                    user.roles = ['admin']
                else:
                    user.roles = ['usuario']
                    
        except Exception as e:
            logger.warning(f"Error cargando roles para {user.usuario}: {str(e)}")
            # Usar rol por defecto basado en el nombre del usuario
            if user.usuario.lower() in ['admin', 'administrador']:
                user.roles = ['admin']
            else:
                user.roles = ['usuario']
        
        logger.info(f"Usuario autenticado exitosamente: {user.usuario}")
        return user
        
    except JWTAuthError as e:
        raise AuthenticationError(f"Token inválido: {str(e)}")
    except Exception as e:
        logger.error(f"Error obteniendo usuario desde token: {str(e)}")
        raise AuthenticationError(f"Error de autenticación: {str(e)}")

def get_dashboard_data(user: UserDB, db: Session) -> Dict[str, Any]:
    """
    Obtiene datos para el dashboard del usuario autenticado
    
    Args:
        user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Diccionario con datos del dashboard
    """
    try:
        # Contar usuarios totales
        user_count = db.query(func.count(Usuarios.codigo)).scalar() or 0
        
        # Obtener actividades recientes (ejemplo)
        recent_activities = db.query(Usuarios).filter(
            Usuarios.activo == True
        ).order_by(Usuarios.codigo.desc()).limit(5).all()
        
        # Formatear actividades
        activities = []
        for activity in recent_activities:
            activities.append({
                "usuario": {"nombre": activity.nombre},
                "action": "se registró en el sistema",
                "timestamp": "hace 2 horas"  # Aquí podrías usar una fecha real
            })
        
        return {
            "user": {
                "codigo": user.codigo,
                "usuario": user.usuario,
                "nombre": user.nombre,
                "mail": user.mail,
                "roles": user.roles,
                "activo": user.activo
            },
            "user_count": user_count,
            "activity_count": len(activities),
            "activities": activities,
            "is_admin": "admin" in user.roles,
            "is_authenticated": True
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo datos del dashboard: {str(e)}")
        # Devolver datos mínimos en caso de error
        return {
            "user": {
                "codigo": user.codigo,
                "usuario": user.usuario,
                "nombre": user.nombre,
                "mail": user.mail,
                "roles": user.roles,
                "activo": user.activo
            },
            "user_count": 0,
            "activity_count": 0,
            "activities": [],
            "is_admin": "admin" in user.roles,
            "is_authenticated": True
        }

async def require_auth_for_template(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency que requiere autenticación para servir plantillas HTML.
    
    Si no hay autenticación válida, redirige automáticamente a la página de login.
    Si hay autenticación válida, devuelve datos completos del usuario y dashboard.
    
    Args:
        request: Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        Diccionario con datos del usuario y dashboard para la plantilla
        
    Raises:
        HTTPException: Redirige a login si no hay autenticación válida
    """
    logger.info(f"Verificando autenticación para: {request.url.path}")
    
    # Extraer token de la petición
    token = extract_token_from_request(request)
    
    if not token:
        logger.warning("No se encontró token en la petición")
        return_url = str(request.url)
        login_url = f"{LOGIN_PAGE_URL}?next={return_url}"
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": login_url}
        )
    
    try:
        # Verificar token y obtener usuario
        user = get_user_from_token(token, db)
        
        # Obtener datos del dashboard
        dashboard_data = get_dashboard_data(user, db)
        
        logger.info(f"Autenticación exitosa para usuario: {user.usuario}")
        return dashboard_data
        
    except AuthenticationError as e:
        logger.warning(f"Error de autenticación: {str(e)}")
        return_url = str(request.url)
        login_url = f"{LOGIN_PAGE_URL}?next={return_url}"
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": login_url}
        )
    except Exception as e:
        logger.error(f"Error inesperado procesando usuario: {str(e)}")
        return_url = str(request.url)
        login_url = f"{LOGIN_PAGE_URL}?next={return_url}"
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": login_url}
        )

async def require_admin_for_template(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency que requiere rol de administrador para servir plantillas HTML.
    
    Combina require_auth_for_template con verificación de rol admin.
    
    Args:
        request: Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        Diccionario con datos del usuario admin y dashboard
        
    Raises:
        HTTPException: Redirige a login o muestra error 403 si no es admin
    """
    # Primero verificar autenticación
    user_data = await require_auth_for_template(request, db)
    
    # Verificar rol de admin
    if not user_data.get("is_admin", False):
        logger.warning(f"Usuario {user_data['user']['usuario']} intentó acceder a área de admin sin permisos")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de administrador requerido"
        )
    
    logger.info(f"Acceso de admin autorizado para: {user_data['user']['usuario']}")
    return user_data

# Función de utilidad para verificar roles específicos
def require_role_for_template(required_role: str):
    """
    Factory function para crear dependencies que requieren roles específicos
    
    Args:
        required_role: Rol requerido (ej: "admin", "user", "moderator")
        
    Returns:
        Dependency function
    """
    async def check_role(
        request: Request,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        # Verificar autenticación
        user_data = await require_auth_for_template(request, db)
        
        # Verificar rol específico
        user_roles = user_data['user'].get('roles', [])
        if required_role.lower() not in user_roles:
            logger.warning(
                f"Usuario {user_data['user']['usuario']} intentó acceder sin rol {required_role}. "
                f"Roles actuales: {user_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol '{required_role}' requerido"
            )
        
        return user_data
    
    return check_role

# Para compatibilidad con el sistema anterior, mantener estas funciones simples
async def get_authenticated_user(request: Request, db: Session = Depends(get_db)) -> UserDB:
    """
    Función simple que solo devuelve el usuario autenticado (sin datos de dashboard)
    Útil para APIs que solo necesitan el usuario
    """
    logger.debug(f"get_authenticated_user called for path: {request.url.path}")
    
    token = extract_token_from_request(request)
    logger.debug(f"Token extracted: {'YES' if token else 'NO'}")
    
    if not token:
        logger.warning("No token found in request")
        raise HTTPException(status_code=401, detail="Token requerido")
    
    try:
        user = get_user_from_token(token, db)
        logger.debug(f"User authenticated: {user.usuario}")
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")

def require_role_api(roles: list):
    """
    Dependency factory para endpoints de API que requieren roles específicos.
    Compatible con autenticación por cookies, headers y query params.
    
    Args:
        roles: Lista de roles permitidos (ej: ["admin", "manager"])
        
    Returns:
        Function que verifica el rol del usuario
    """
    async def check_role(request: Request, db: Session = Depends(get_db)) -> UserDB:
        try:
            # Obtener usuario autenticado usando el sistema de cookies/headers/query
            user = await get_authenticated_user(request, db)
              # Verificar si el usuario tiene al menos uno de los roles requeridos
            user_roles = []
            if hasattr(user, 'roles') and user.roles:
                # Los roles pueden ser strings o objetos, manejar ambos casos
                if isinstance(user.roles, list):
                    user_roles = []
                    for role in user.roles:
                        if isinstance(role, str):
                            user_roles.append(role.lower())
                        elif hasattr(role, 'nombre'):
                            user_roles.append(role.nombre.lower())
                        else:
                            user_roles.append(str(role).lower())
                else:
                    user_roles = [str(user.roles).lower()]
            
            # Verificar rol
            has_required_role = any(role.lower() in user_roles for role in roles)
            
            if not has_required_role:
                logger.warning(
                    f"Usuario {user.usuario} intentó acceder sin roles {roles}. "
                    f"Roles actuales: {user_roles}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere uno de estos roles: {roles}"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error en verificación de rol: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación"
            )
    
    return check_role
