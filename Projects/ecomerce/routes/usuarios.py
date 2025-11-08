from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template
from ..middleware.ecommerce_auth import require_ecommerce_auth, get_current_ecommerce_user
import logging
import httpx

# Imports locales del servicio
from ..schemas.usuarios import UsuariosCreate, UsuariosUpdate, UsuariosRead, UsuariosProfile, UserProfileComplete
from ..Controllers.usuarios import (
    create_usuarios,
    get_usuarios,
    gets_usuarios,
    update_usuarios,
    delete_usuarios,
    get_user_profile,
    change_user_password,
    get_user_orders,
    get_user_active_cart,
    get_user_budgets,
    get_order_details
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["usuarios"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=UsuariosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_usuarios(usuarios: UsuariosCreate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        usuarios_payload = usuarios.model_dump(exclude_unset=True, exclude_none=True)
        
        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in usuarios_payload and usuarios_payload['id'] is None:
            del usuarios_payload['id']
        
        db_usuarios = create_usuarios(db=db, usuarios=usuarios_payload, user_data=user_data, request=request)
        return UsuariosRead.model_validate(db_usuarios)
    except Exception as e:
        logger.error(f"Error al crear Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=UsuariosRead)
async def routes_get_usuarios_id(id: int, db: Session = Depends(get_db)):
    try:
        db_usuarios = get_usuarios(db, id)
        if not db_usuarios:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: usuarios no encontrado")
        return UsuariosRead.model_validate(db_usuarios)
    except Exception as e:
        logger.error(f"Error al obtener Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[UsuariosRead])
async def routes_gets_usuarios_all(db: Session = Depends(get_db)):
    try:
        db_usuarios = gets_usuarios(db)
        # Una lista vacía es un resultado válido, no un error
        return [UsuariosRead.model_validate(usuarios) for usuarios in db_usuarios]
    except Exception as e:
        logger.error(f"Error al obtener registros de Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=UsuariosRead)
async def routes_delete_usuarios_numero(id: int, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        resultado_usuarios = get_usuarios(db, id)
        if not resultado_usuarios:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: usuarios no encontrado")
        db_usuarios = delete_usuarios(db, id, user_data=user_data, request=request)
        return UsuariosRead.model_validate(db_usuarios)
    except Exception as e:
        logger.error(f"Error al eliminar Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=UsuariosRead)
async def routes_update_usuarios(id: int, usuarios: UsuariosUpdate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Usuarios con id = {id}")
    try:
        usuarios_data = usuarios.model_dump()
        db_usuarios = update_usuarios(db=db, id=id, usuarios_data=usuarios_data, user_data=user_data, request=request)
        return UsuariosRead.model_validate(db_usuarios)
    except Exception as e:
        logger.error(f"Error al actualizar Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/profile")
async def routes_get_user_profile(user_data: dict = Depends(get_current_ecommerce_user), db: Session = Depends(get_db)):
    try:
        logger.info(f"Obteniendo perfil para usuario: {user_data}")
        user_email = user_data["user"]["email"]  # Email del usuario de e-commerce
        logger.info(f"Email extraído: {user_email}")
        
        profile_data = get_user_profile(db, user_email)
        logger.info(f"Datos de perfil obtenidos: {profile_data}")
        
        # Convertir datetime a string para evitar problemas de serialización
        if profile_data.get("user") and profile_data["user"].get("created_at"):
            profile_data["user"]["created_at"] = str(profile_data["user"]["created_at"])
        
        # El profile_data ya viene como dict desde el controlador
        return profile_data
    except KeyError as e:
        logger.error(f"Error de estructura de datos en perfil: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error de estructura: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener perfil del usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el perfil: {str(e)}")


@router.put("/profile")
async def routes_update_user_profile(usuarios: UsuariosUpdate, user_data: dict = Depends(get_current_ecommerce_user), db: Session = Depends(get_db)):
    try:
        user_email = user_data["user"]["email"]
        # Obtener el id del usuario e-commerce por email
        user_result = db.execute(
            text("SELECT id FROM ecomerce_usuarios WHERE email = :email"),
            {"email": user_email}
        ).first()
        if not user_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        user_id = user_result[0]

        usuarios_data = usuarios.model_dump(exclude_unset=True, exclude_none=True)
        db_usuarios = update_usuarios(db=db, id=user_id, usuarios_data=usuarios_data, user_data=user_data, request=None)
        
        # Convertir a diccionario para responder
        return {
            "id": db_usuarios.id,
            "nombre": db_usuarios.nombre,
            "apellido": db_usuarios.apellido if hasattr(db_usuarios, 'apellido') else None,
            "email": db_usuarios.email,
            "telefono": db_usuarios.telefono if hasattr(db_usuarios, 'telefono') else None,
            "direccion": db_usuarios.direccion if hasattr(db_usuarios, 'direccion') else None,
            "google_maps_link": db_usuarios.google_maps_link if hasattr(db_usuarios, 'google_maps_link') else None,
            "ciudad": db_usuarios.ciudad if hasattr(db_usuarios, 'ciudad') else None,
            "provincia": db_usuarios.provincia if hasattr(db_usuarios, 'provincia') else None,
            "pais": db_usuarios.pais if hasattr(db_usuarios, 'pais') else None,
            "created_at": str(db_usuarios.created_at) if hasattr(db_usuarios, 'created_at') else None,
            "active": db_usuarios.active if hasattr(db_usuarios, 'active') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar perfil del usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el perfil: {str(e)}")


@router.post("/change-password")
async def routes_change_user_password(
    password_data: dict,
    user_data: dict = Depends(get_current_ecommerce_user),
    db: Session = Depends(get_db)
):
    try:
        user_email = user_data["user"]["email"]
        current_password = password_data.get("current_password")
        new_password = password_data.get("new_password")

        if not current_password or not new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual y nueva son requeridas")

        if len(new_password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La nueva contraseña debe tener al menos 8 caracteres")

        result = change_user_password(db, user_email, current_password, new_password)
        return result

    except Exception as e:
        logger.error(f"Error al cambiar contraseña: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cambiar contraseña.")


@router.get("/pedidos/user")
async def routes_get_user_orders(user_data: dict = Depends(get_current_ecommerce_user), db: Session = Depends(get_db)):
    try:
        user_email = user_data["user"]["email"]

        # Obtener el id del usuario
        user_result = db.execute(
            text("SELECT id FROM ecomerce_usuarios WHERE email = :email"),
            {"email": user_email}
        ).first()

        if not user_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        user_id = user_result[0]
        orders = get_user_orders(db, user_id)
        return orders

    except Exception as e:
        logger.error(f"Error al obtener pedidos del usuario: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener pedidos.")


@router.get("/pedidos/{pedido_id}")
async def routes_get_order_details(pedido_id: int, user_data: dict = Depends(get_current_ecommerce_user), db: Session = Depends(get_db)):
    try:
        user_email = user_data["user"]["email"]

        # Obtener el id del usuario
        user_result = db.execute(
            text("SELECT id FROM ecomerce_usuarios WHERE email = :email"),
            {"email": user_email}
        ).first()

        if not user_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        user_id = user_result[0]
        order_details = get_order_details(db, pedido_id, user_id)
        return order_details

    except Exception as e:
        logger.error(f"Error al obtener detalles del pedido: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener detalles del pedido.")


@router.get("/carritos/active")
async def routes_get_user_active_cart(user_data: dict = Depends(get_current_ecommerce_user)):
    """
    Obtiene el carrito activo del usuario con autenticación.
    """
    db = None
    try:
        # Crear sesión de base de datos manualmente
        from db.database import SessionLocal
        db = SessionLocal()

        user_email = user_data["user"]["email"]

        # Obtener el id del usuario
        user_result = db.execute(
            text("SELECT id FROM ecomerce_usuarios WHERE email = :email"),
            {"email": user_email}
        ).first()

        if not user_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        user_id = user_result[0]
        cart = get_user_active_cart(db, user_id)
        return cart if cart else {"message": "No hay carrito activo"}

    except Exception as e:
        logger.error(f"Error al obtener carrito activo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener carrito.")
    finally:
        if db:
            db.close()


@router.get("/presupuestos/user")
async def routes_get_user_budgets(user_data: dict = Depends(get_current_ecommerce_user), db: Session = Depends(get_db)):
    try:
        user_email = user_data["user"]["email"]
        budgets = get_user_budgets(db, user_email)
        return budgets

    except Exception as e:
        logger.error(f"Error al obtener presupuestos del usuario: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener presupuestos.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina(user_data: dict = Depends(require_auth_for_template)):
    """
    Página de administración de usuarios de e-commerce.
    Requiere autenticación de administrador del sistema de configuración.
    """
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"usuarios2.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")


@router.get("/perfil", response_class=HTMLResponse)
async def get_perfil_pagina(user_data: dict = Depends(require_ecommerce_auth)):
    """
    Página de perfil del usuario de e-commerce.
    Requiere autenticación con token de e-commerce (ecommerce_token).
    """
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"perfil.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML del perfil: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML del perfil.")


@router.get("/pedidos", response_class=HTMLResponse)
async def get_pedidos_pagina(user_data: dict = Depends(require_ecommerce_auth)):
    """
    Página de pedidos del usuario de e-commerce.
    Requiere autenticación con token de e-commerce (ecommerce_token).
    """
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"pedidos.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML de pedidos.")


@router.get("/geocode", dependencies=[])
async def geocode_address(q: str):
    """
    Endpoint para geocodificar direcciones usando Nominatim (OpenStreetMap).
    Evita problemas de CORS haciendo la request desde el servidor.
    """
    try:
        if not q or not q.strip():
            return {"error": "Dirección vacía"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "format": "json",
                    "q": q,
                    "limit": 1
                },
                headers={
                    "User-Agent": "Ecommerce-Perfil/1.0 (https://github.com/JuanS1mon/nuevo-proyecto)"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "lat": data[0]["lat"],
                        "lon": data[0]["lon"],
                        "display_name": data[0]["display_name"],
                        "type": data[0]["type"],
                        "importance": data[0]["importance"]
                    }
                else:
                    return {"error": "Dirección no encontrada"}
            else:
                logger.error(f"Error en Nominatim: {response.status_code} - {response.text}")
                return {"error": f"Error del servicio: {response.status_code}"}

    except httpx.TimeoutException:
        logger.error("Timeout en geocodificación")
        return {"error": "Timeout en la geocodificación"}
    except Exception as e:
        logger.error(f"Error en geocodificación: {e}")
        return {"error": f"Error interno: {str(e)}"}
