# Imports necesarios
from datetime import date, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request, status, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sql_app.Services.security.utils import encriptar_clave
from sql_app.Services.security.jwt_auth import get_current_user, require_admin
from sql_app.Services.security.auth_middleware import require_admin_for_template, get_authenticated_user
from sql_app.db.database import get_db
from sql_app.db.models.config.usuarios import Usuarios
from sql_app.db.schemas.config.Usuarios import UserDB
import base64
from PIL import Image
import io


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
async def admin_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Página de admin - Versión simplificada para debug
    """
    try:
        # Verificar si el middleware ya validó la autenticación
        is_authenticated = getattr(request.state, 'authenticated', False)
        token_data = getattr(request.state, 'token_data', None)
        
        print(f"🔍 ADMIN DEBUG: is_authenticated = {is_authenticated}")
        print(f"🔍 ADMIN DEBUG: token_data = {token_data}")
        print(f"🔍 ADMIN DEBUG: request.state = {request.state.__dict__}")
        
        if not is_authenticated:
            print("❌ Usuario no autenticado, redirigiendo...")
            return RedirectResponse(url="/loginpage", status_code=303)
        
        username = getattr(token_data, 'username', 'Unknown') if token_data else 'Unknown'
        print(f"✅ Usuario autenticado: {username}")
        
        # Datos mínimos para la template
        template_data = {
            "request": request,
            "user": {
                "usuario": username,
                "nombre": username,
                "mail": f"{username}@example.com",
                "roles": ["admin"],
                "activo": True
            },
            "user_count": 1,
            "activity_count": 0,
            "activities": [],
            "is_admin": True,
            "is_authenticated": True
        }
        
        print(f"🔍 Renderizando template con datos: {template_data.keys()}")
        return templates.TemplateResponse("admin.html", template_data)
        
    except Exception as e:
        print(f"❌ ERROR EN ADMIN: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error en admin: {str(e)}"
        )

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
    try:
        print("🔍 DEBUG PERFIL: Datos del usuario recibidos:")
        print(f"user_data keys: {list(user_data.keys())}")
        print(f"user data: {user_data.get('user', {})}")
        
        # Asegurar que el usuario tenga todos los campos necesarios
        user = user_data.get('user', {})
        
        # Completar campos faltantes con valores por defecto
        if not user.get('telefono'):
            user['telefono'] = ''
        if not user.get('direccion'):
            user['direccion'] = ''
        if not user.get('fecha_nacimiento'):
            user['fecha_nacimiento'] = ''
        if not user.get('imagen_perfil'):
            user['imagen_perfil'] = ''
        if not isinstance(user.get('roles'), list):
            # Si roles no es una lista, convertirlo en una lista de objetos con nombre
            if 'admin' in str(user.get('roles', '')).lower():
                user['roles'] = [{'nombre': 'Administrador'}]
            else:
                user['roles'] = [{'nombre': 'Usuario'}]
        elif user['roles'] and isinstance(user['roles'][0], str):
            # Si es una lista de strings, convertir a objetos
            user['roles'] = [{'nombre': role.title()} for role in user['roles']]
        
        print(f"🔍 DEBUG PERFIL: Usuario procesado: {user}")
        
        return templates.TemplateResponse(
            "html/usuarios/usuario_admin.html",
            {
                "request": request, 
                **user_data
            }
        )
        
    except Exception as e:
        print(f"❌ ERROR EN PERFIL: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error cargando perfil: {str(e)}"
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
    imagen_perfil: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user_data: Dict[str, Any] = Depends(require_admin_for_template)
):
    """Actualización del perfil de usuario - AUTENTICACIÓN BACKEND"""
    try:
        user = user_data.get('user', {})
        user_id = user.get('codigo')
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario no válido")
        
        # Buscar usuario en la base de datos
        db_user = db.query(Usuarios).filter(Usuarios.codigo == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Actualizar campos
        db_user.nombre = nombre
        if hasattr(db_user, 'telefono'):
            db_user.telefono = telefono
        db_user.mail = email
        if hasattr(db_user, 'direccion'):
            db_user.direccion = direccion
        if fecha_nacimiento and hasattr(db_user, 'fecha_nacimiento'):
            db_user.fecha_nacimiento = fecha_nacimiento
        
        # Actualizar contraseña si se proporcionó
        if password and len(password.strip()) > 0:
            from sql_app.Services.security.utils import encriptar_clave
            db_user.clave = encriptar_clave(password)

        # Procesar imagen de perfil si se proporcionó
        if imagen_perfil and imagen_perfil.size > 0:
            try:
                # Leer el contenido de la imagen
                contents = await imagen_perfil.read()
                
                # Validar tamaño máximo (10MB)
                if len(contents) > 10 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail="La imagen es demasiado grande. Máximo 10MB.")
                
                # Procesar imagen con PIL para comprimir
                image = Image.open(io.BytesIO(contents))
                
                # Redimensionar si es muy grande (máximo 400x400)
                if image.width > 400 or image.height > 400:
                    image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                # Convertir a RGB si está en otro formato
                if image.mode in ('RGBA', 'P'):
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = rgb_image
                
                # Comprimir y convertir a base64
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=85, optimize=True)
                compressed_image = output.getvalue()
                
                # Convertir a base64 para almacenar en la base de datos
                imagen_base64 = base64.b64encode(compressed_image).decode('utf-8')
                
                # Actualizar en la base de datos
                if hasattr(db_user, 'imagen_perfil'):
                    db_user.imagen_perfil = imagen_base64
                    
            except Exception as e:
                print(f"Error procesando imagen: {str(e)}")
                # No detener el proceso por un error de imagen, solo mostrar aviso
                pass

        # Guardar cambios
        db.commit()
        db.refresh(db_user)
        
        message = "Perfil actualizado exitosamente"
        
        # Actualizar los datos del usuario para mostrar en el template
        user_data['user'].update({
            'nombre': nombre,
            'telefono': telefono,
            'mail': email,
            'direccion': direccion,
            'fecha_nacimiento': fecha_nacimiento,
            'imagen_perfil': getattr(db_user, 'imagen_perfil', None)
        })
        user_data['message'] = message

        return templates.TemplateResponse(
            "html/usuarios/usuario_admin.html",
            {
                "request": request, 
                **user_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR ACTUALIZANDO PERFIL: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el perfil: {str(e)}")

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

# ============================================================================
# ROUTER DEBUG: Endpoint de admin simplificado para diagnóstico
# ============================================================================

@router.get("/simple-debug")
async def simple_admin_debug(request: Request):
    """Endpoint de debug sin autenticación para verificar básico"""
    return {
        "message": "Endpoint debug sin autenticación funcionando",
        "url": str(request.url),
        "cookies": dict(request.cookies),
        "has_access_token": "access_token" in request.cookies
    }