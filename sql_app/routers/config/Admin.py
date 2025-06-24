# Imports necesarios
from datetime import date, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sql_app.Services.security.utils import encriptar_clave
from sql_app.Services.security.jwt_auth import get_current_user, require_admin
from sql_app.Services.security.auth_middleware import require_admin_for_template, get_authenticated_user
from sql_app.db.database import get_db
from sql_app.db.models.config.usuarios import Usuarios
from sql_app.db.schemas.config.Usuarios import UserDB


# Definir la instancia de Jinja2Templates
templates = Jinja2Templates(directory="sql_app/static")

# Definir el router directamente
router = APIRouter(
    include_in_schema=False,
    prefix="/admin",
    tags=["Admin"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "Ruta no encontrada"}}
)

@router.get("")
async def admin_page(request: Request, db: Session = Depends(get_db)):
    """
    Página de admin - Renderizado limpio, autenticación gestionada por middleware
    """
    try:
        # Aquí podrías obtener datos adicionales del usuario si lo necesitas
        # Por ejemplo, desde request.state.token_data si lo guardas en el middleware
        user_data = {}
        # Si necesitas datos del usuario autenticado:
        # token_data = getattr(request.state, 'token_data', None)
        # if token_data:
        #     user_data["user"] = {"usuario": token_data.username}
        return templates.TemplateResponse(
            "admin.html",
            {"request": request, **user_data}
        )
    except Exception as e:
        # Manejo de error simple
        return RedirectResponse(url="/loginpage", status_code=303)

@router.get("/data")
async def admin_data(
        current_user: UserDB = Depends(require_admin)
    ):
    """
    API protegida para obtener datos del usuario admin.
    Requiere token JWT válido.
    """
    print("=========== API DE DATOS ADMIN ===========")
    print(f"Usuario autenticado: {current_user.usuario}")
    print(f"Roles: {current_user.roles}")
    
    return {
        "user": {
            "username": current_user.usuario,
            "nombre": current_user.nombre,
            "email": current_user.mail,
            "roles": current_user.roles,
            "activo": current_user.activo
        },
        "message": "Datos de admin obtenidos exitosamente"
    }

@router.get("/perfil")
async def user_perfil(
    request: Request,
    user_data: Dict[str, Any] = Depends(require_admin_for_template)
):
    """Página de perfil de usuario - AUTENTICACIÓN BACKEND"""
    return templates.TemplateResponse(
        "/usuarios/usuario_admin.html",
        {
            "request": request, 
            **user_data
        }
    )

@router.post("/perfil")
async def update_perfil(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    direccion: str = Form(...),
    fecha_nacimiento: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: UserDB = Depends(get_authenticated_user)
):
    """Actualización del perfil de usuario - AUTENTICACIÓN BACKEND"""
    db_user = db.query(Usuarios).filter(Usuarios.codigo == user.codigo).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_user.nombre = nombre
    db_user.telefono = telefono
    db_user.mail = email
    db_user.direccion = direccion
    if fecha_nacimiento:
        db_user.fecha_nacimiento = fecha_nacimiento
    if password:
        db_user.clave = encriptar_clave(password)

    try:
        db.commit()
        db.refresh(db_user)
        message = "Perfil actualizado exitosamente"
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el perfil: {str(e)}")

    return templates.TemplateResponse(
        "/usuarios/usuario_admin.html",
        {
            "request": request, 
            "user": user, 
            "message": message,
            "is_authenticated": True,
            "is_admin": "admin" in getattr(user, 'roles', [])
        }
    )

# ============================================================================
# ROUTER DEBUG: Endpoint de admin simplificado para diagnóstico
# ============================================================================

@router.get("/debug")
async def admin_debug(
    request: Request,
    current_user: UserDB = Depends(require_admin)
):
    """Endpoint de debug simplificado para admin"""
    try:
        print("🔍 DEBUG /admin/debug - Iniciando...")
        print(f"Usuario: {current_user}")
        print(f"Request: {request}")
        
        # Verificar usuario
        if not current_user:
            print("❌ Usuario no encontrado")
            raise HTTPException(status_code=401, detail="Usuario no autenticado")
        
        print(f"✅ Usuario válido: {current_user.usuario}")
        
        # Intentar devolver JSON simple primero
        return {
            "message": "Debug exitoso",
            "user": {
                "usuario": current_user.usuario,
                "nombre": current_user.nombre,
                "roles": getattr(current_user, 'roles', [])
            }
        }
        
    except Exception as e:
        print(f"❌ Error en debug: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error debug: {str(e)}")

@router.get("/test-template")
async def test_template(request: Request):
    """Endpoint de prueba para verificar que Jinja2 funciona"""
    test_data = {
        "user": {
            "nombre": "Usuario de Prueba",
            "usuario": "test"
        },
        "user_count": 42,
        "activity_count": 5,
        "activities": [],
        "is_admin": True
    }
    
    try:
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                **test_data
            }
        )
    except Exception as e:
        return f"Error renderizando template: {str(e)}"

@router.get("/debug-cookies")
async def debug_cookies(request: Request):
    """Debug para verificar cookies"""
    return {
        "cookies_recibidas": dict(request.cookies),
        "headers": dict(request.headers),
        "url": str(request.url)
    }