from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template, get_authenticated_user
from security.ecommerce_auth import get_current_ecommerce_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.schemas.config.Usuarios import UserDB
import logging
import traceback

# Imports locales del servicio
from ..schemas.carrito_items import Carrito_itemsCreate, Carrito_itemsUpdate, Carrito_itemsRead, Carrito_itemsSimpleCreate
from ..models.carrito_items import EcomerceCarrito_items
from ..Controllers.carrito_items import (
    create_carrito_items,
    get_carrito_items,
    gets_carrito_items,
    update_carrito_items,
    delete_carrito_items
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["carrito_items"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

def get_current_ecommerce_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """
    Dependencia para obtener el usuario ecommerce actual
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido"
        )

    user = get_current_ecommerce_user(credentials.credentials, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    return user

@router.post("/", response_model=Carrito_itemsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_carrito_items(carrito_items: Carrito_itemsCreate, request: Request, user: dict = Depends(get_current_ecommerce_user_dependency), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        carrito_items_payload = carrito_items.model_dump(exclude_unset=True, exclude_none=True)

        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in carrito_items_payload and carrito_items_payload['id'] is None:
            del carrito_items_payload['id']

        # Crear user_data dict para compatibilidad con el controlador
        user_data = {
            "codigo": user["id"],  # Usar 'id' en lugar de 'codigo' para usuarios ecommerce
            "usuario": user["email"],  # Usar email como usuario
            "nombre": user["nombre"],
            "email": user["email"],
            "roles": []  # Usuarios ecommerce no tienen roles del sistema
        }

        db_carrito_items = create_carrito_items(db=db, carrito_items=carrito_items_payload, user_data=user_data, request=request)
        return Carrito_itemsRead.model_validate(db_carrito_items)
    except Exception as e:
        logger.error(f"Error al crear Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.post("/simple", response_model=Carrito_itemsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_carrito_items_simple(
    item_data: Carrito_itemsSimpleCreate,
    request: Request,
    user: dict = Depends(get_current_ecommerce_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Ruta simplificada para agregar productos al carrito.
    Crea automáticamente el carrito si no existe uno activo.
    """
    try:
        logger.info(f"Datos recibidos en /simple: {item_data}")
        logger.info(f"Tipos de datos: product_id={type(item_data.product_id)}, quantity={type(item_data.quantity)}, price={type(item_data.price)}")

        product_id = item_data.product_id
        quantity = item_data.quantity
        price = item_data.price

        logger.info(f"Valores extraídos: product_id={product_id}, quantity={quantity}, price={price}")

        # Validaciones adicionales
        if not isinstance(product_id, int) or product_id <= 0:
            logger.error(f"product_id inválido: {product_id} (tipo: {type(product_id)})")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de producto inválido")

        if not isinstance(quantity, int) or quantity <= 0:
            logger.error(f"quantity inválido: {quantity} (tipo: {type(quantity)})")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cantidad inválida")

        if not isinstance(price, (int, float)) or price < 0:
            logger.error(f"price inválido: {price} (tipo: {type(price)})")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Precio inválido")

        # Convertir precio a int para compatibilidad con el modelo
        price_int = int(price) if price else 0

        logger.info(f"Usando valores finales: product_id={product_id}, quantity={quantity}, price_int={price_int}")

        # Usar la nueva clase Cart
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
        from Services.cart_service import Cart

        cart = Cart(db, user["id"])  # Usar user["id"] para usuarios ecommerce
        item = cart.add_item(product_id, quantity, price_int)

        logger.info(f"Item agregado exitosamente: {item}")

        # Crear objeto de respuesta
        from ..models.carrito_items import EcomerceCarrito_items
        db_item = EcomerceCarrito_items()
        db_item.id = item['id']
        db_item.id_carrito = item['id_carrito']
        db_item.id_producto = item['id_producto']
        db_item.cantidad = item['cantidad']
        db_item.precio_unitario = item['precio_unitario']

        return Carrito_itemsRead.model_validate(db_item)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al agregar producto al carrito: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al agregar producto al carrito.")


@router.get("/id/{id}", response_model=Carrito_itemsRead)
async def routes_get_carrito_items_id(id: int, db: Session = Depends(get_db)):
    try:
        db_carrito_items = get_carrito_items(db, id)
        if not db_carrito_items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: carrito_items no encontrado")
        return Carrito_itemsRead.model_validate(db_carrito_items)
    except Exception as e:
        logger.error(f"Error al obtener Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Carrito_itemsRead])
async def routes_gets_carrito_items_all(db: Session = Depends(get_db)):
    try:
        db_carrito_items = gets_carrito_items(db)
        # Una lista vacía es un resultado válido, no un error
        return [Carrito_itemsRead.model_validate(carrito_items) for carrito_items in db_carrito_items]
    except Exception as e:
        logger.error(f"Error al obtener registros de Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Carrito_itemsRead)
async def routes_delete_carrito_items_numero(id: int, request: Request, user: dict = Depends(get_current_ecommerce_user_dependency), db: Session = Depends(get_db)):
    try:
        # Verificar que el item pertenece al usuario actual
        item_result = db.execute(
            text("""
                SELECT ci.id, ci.id_carrito, ci.id_producto, ci.cantidad, ci.precio_unitario
                FROM ecomerce_carrito_items ci
                INNER JOIN ecomerce_carritos c ON ci.id_carrito = c.id
                WHERE ci.id = :item_id AND c.id_usuario = :user_id AND c.estado = 'activo'
            """),
            {"item_id": id, "user_id": user["id"]}  # Usar user["id"] para usuarios ecommerce
        ).first()

        if not item_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado o no pertenece al usuario")

        # Eliminar el item
        delete_query = text("""
            DELETE FROM ecomerce_carrito_items
            OUTPUT DELETED.id, DELETED.id_carrito, DELETED.id_producto, DELETED.cantidad, DELETED.precio_unitario
            WHERE id = :item_id
        """)
        result = db.execute(delete_query, {"item_id": id})
        row = result.first()

        if not row:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el item")

        db.commit()

        # Crear objeto de respuesta
        from ..models.carrito_items import EcomerceCarrito_items
        db_item = EcomerceCarrito_items()
        db_item.id = row[0]
        db_item.id_carrito = row[1]
        db_item.id_producto = row[2]
        db_item.cantidad = row[3]
        db_item.precio_unitario = row[4]

        return Carrito_itemsRead.model_validate(db_item)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Carrito_itemsRead)
async def routes_update_carrito_items(id: int, carrito_items: Carrito_itemsUpdate, request: Request, user: dict = Depends(get_current_ecommerce_user_dependency), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Carrito_items con id = {id}")
    try:
        # Verificar que el item pertenece al usuario actual
        item_result = db.execute(
            text("""
                SELECT ci.id, ci.id_carrito, ci.id_producto, ci.cantidad, ci.precio_unitario
                FROM ecomerce_carrito_items ci
                INNER JOIN ecomerce_carritos c ON ci.id_carrito = c.id
                WHERE ci.id = :item_id AND c.id_usuario = :user_id AND c.estado = 'activo'
            """),
            {"item_id": id, "user_id": user["id"]}  # Usar user["id"] para usuarios ecommerce
        ).first()

        if not item_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado o no pertenece al usuario")

        # Actualizar la cantidad
        new_quantity = carrito_items.cantidad
        if new_quantity <= 0:
            # Si la cantidad es 0 o menor, eliminar el item
            return await routes_delete_carrito_items_numero(id, request, user, db)

        update_query = text("""
            UPDATE ecomerce_carrito_items
            SET cantidad = :quantity
            OUTPUT INSERTED.id, INSERTED.id_carrito, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario
            WHERE id = :item_id
        """)
        result = db.execute(update_query, {"quantity": new_quantity, "item_id": id})
        row = result.first()

        if not row:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el item")

        db.commit()

        # Crear objeto de respuesta
        from ..models.carrito_items import EcomerceCarrito_items
        db_item = EcomerceCarrito_items()
        db_item.id = row[0]
        db_item.id_carrito = row[1]
        db_item.id_producto = row[2]
        db_item.cantidad = row[3]
        db_item.precio_unitario = row[4]

        return Carrito_itemsRead.model_validate(db_item)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"carrito_items.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")


@router.get("/carrito/{carrito_id}", response_model=List[Carrito_itemsRead])
async def routes_get_carrito_items_por_carrito(carrito_id: int, user: dict = Depends(get_current_ecommerce_user_dependency), db: Session = Depends(get_db)):
    try:
        # Verificar que el carrito pertenece al usuario actual
        cart_check = db.execute(
            text("SELECT id FROM ecomerce_carritos WHERE id = :carrito_id AND id_usuario = :user_id"),
            {"carrito_id": carrito_id, "user_id": user["id"]}
        ).first()

        if not cart_check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado o no pertenece al usuario")

        # Usar la nueva clase Cart para obtener los items
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
        from Services.cart_service import Cart

        cart = Cart(db, user["id"])

        # Convertir los items a objetos de respuesta
        items = []
        for item in cart.items:
            from ..models.carrito_items import EcomerceCarrito_items
            db_item = EcomerceCarrito_items()
            db_item.id = item['id']
            db_item.id_carrito = item['id_carrito']
            db_item.id_producto = item['id_producto']
            db_item.cantidad = item['cantidad']
            db_item.precio_unitario = item['precio_unitario']
            items.append(Carrito_itemsRead.model_validate(db_item))

        return items
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener items del carrito: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los items del carrito.")
