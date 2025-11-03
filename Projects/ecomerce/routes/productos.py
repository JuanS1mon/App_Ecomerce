from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template
import logging

# Imports locales del servicio
from ..schemas.productos import ProductosCreate, ProductosUpdate, ProductosRead
from ..Controllers.productos import (
    create_productos,
    get_productos,
    gets_productos,
    update_productos,
    delete_productos
)
from ..middleware.ecommerce_auth import require_ecommerce_auth

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["productos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ProductosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_productos(productos: ProductosCreate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        productos_payload = productos.model_dump(exclude_unset=True, exclude_none=True)
        
        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in productos_payload and productos_payload['id'] is None:
            del productos_payload['id']
        
        db_productos = create_productos(db=db, productos=productos_payload, user_data=user_data, request=request)
        return ProductosRead.model_validate(db_productos)
    except Exception as e:
        logger.error(f"Error al crear Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=ProductosRead)
async def routes_get_productos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_productos = get_productos(db, id)
        if not db_productos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: productos no encontrado")
        return ProductosRead.model_validate(db_productos)
    except Exception as e:
        logger.error(f"Error al obtener Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[ProductosRead])
async def routes_gets_productos_all(db: Session = Depends(get_db)):
    try:
        db_productos = gets_productos(db)
        # Una lista vacía es un resultado válido, no un error
        return [ProductosRead.model_validate(productos) for productos in db_productos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=ProductosRead)
async def routes_delete_productos_numero(id: int, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        resultado_productos = get_productos(db, id)
        if not resultado_productos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: productos no encontrado")
        db_productos = delete_productos(db, id, user_data=user_data, request=request)
        return ProductosRead.model_validate(db_productos)
    except Exception as e:
        logger.error(f"Error al eliminar Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=ProductosRead)
async def routes_update_productos(id: int, productos: ProductosUpdate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Productos con id = {id}")
    try:
        productos_data = productos.model_dump()
        db_productos = update_productos(db=db, id=id, productos_data=productos_data, user_data=user_data, request=request)
        return ProductosRead.model_validate(db_productos)
    except Exception as e:
        logger.error(f"Error al actualizar Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/tienda", response_class=HTMLResponse)
async def get_tienda_publica():
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"productos_tienda.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de tienda: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML de tienda.")


@router.get("/publicos", response_class=HTMLResponse)
async def get_productos_publicos_pagina():
    """
    Página HTML que muestra los productos públicos (sin requerir login)
    """
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"productos_tienda.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de productos públicos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML de productos públicos.")


@router.get("/api/publicos", response_model=List[ProductosRead])
async def routes_gets_productos_publicos_api(db: Session = Depends(get_db)):
    """
    API que devuelve los productos públicos en formato JSON
    """
    try:
        # Obtener todos los productos
        db_productos = gets_productos(db)
        # Filtrar solo productos activos
        productos_activos = [p for p in db_productos if getattr(p, 'active', True)]
        return [ProductosRead.model_validate(productos) for productos in productos_activos]
    except Exception as e:
        logger.error(f"Error al obtener productos públicos API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los productos públicos.")


@router.get("/admin", response_class=HTMLResponse)
async def get_admin_productos(request: Request, user_data: dict = Depends(require_auth_for_template)):
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"productos.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de administración: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML de administración.")


@router.get("/detalle/{id}", response_class=HTMLResponse)
async def get_detalle_producto(id: int):
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"producto_detalle.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de detalle de producto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML de detalle de producto.")


@router.get("/publico/{id}", response_model=ProductosRead)
async def routes_get_producto_publico(id: int, db: Session = Depends(get_db)):
    try:
        db_productos = get_productos(db, id)
        if not db_productos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        # Verificar que el producto esté activo
        if not getattr(db_productos, 'active', True):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        # Convertir a diccionario para asegurar que se serialice correctamente
        product_dict = {
            "id": db_productos.id,
            "codigo": db_productos.codigo,
            "nombre": db_productos.nombre,
            "descripcion": db_productos.descripcion,
            "id_categoria": db_productos.id_categoria,
            "precio": db_productos.precio,
            "imagen_url": db_productos.imagen_url,
            "active": db_productos.active
        }

        return product_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener producto público: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el producto público.")
