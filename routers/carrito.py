from fastapi import APIRouter, HTTPException, Depends, Form, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy import text
from db.database import get_db
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security.ecommerce_auth import get_current_ecommerce_user
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Modelos Pydantic para validación
class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1
    price: float = 0.0
    model_config = ConfigDict(from_attributes=True)

class UpdateCartItemRequest(BaseModel):
    cantidad: int
    model_config = ConfigDict(from_attributes=True)

# =============================
# CARRITO - Rutas principales
# =============================

@router.post("/test")
async def test_endpoint(
    data: dict = Body(...)
):
    """
    Endpoint de prueba para verificar parsing JSON
    """
    print(f"Received data: {data}")
    return {"received": data, "status": "ok"}

@router.post("/carrito_items/simple")
async def add_to_cart_simple(
    cart_request: AddToCartRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Agrega un producto al carrito de forma simple (crea carrito si no existe)
    """
    try:
        print(f"Received cart_request: {cart_request}")  # Debug
        
        # Obtener usuario del token JWT
        user = get_current_ecommerce_user(credentials.credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")

        user_id = user['id']
        product_id = cart_request.product_id
        quantity = cart_request.quantity
        price = cart_request.price

        # Verificar que el producto existe y está activo
        product_result = db.execute(text("""
            SELECT id, precio, nombre FROM ecomerce_productos
            WHERE id = :product_id AND active = 1
        """), {"product_id": product_id})

        product_rows = product_result.fetchall()
        if not product_rows:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        product_row = product_rows[0]

        # Usar el precio del producto si no se especificó uno
        if price <= 0:
            price = float(product_row[1])

        # Buscar carrito activo del usuario
        cart_result = db.execute(text("""
            SELECT TOP 1 id FROM ecomerce_carritos
            WHERE id_usuario = :user_id AND estado = 'activo'
            ORDER BY created_at DESC
        """), {"user_id": user_id})

        cart_rows = cart_result.fetchall()
        cart_id = None

        if cart_rows:
            # Usar carrito existente
            cart_id = cart_rows[0][0]
        else:
            # Crear nuevo carrito
            db.execute(text("""
                INSERT INTO ecomerce_carritos (id_usuario, estado, created_at)
                VALUES (:user_id, 'activo', :created_at)
            """), {
                "user_id": user_id,
                "created_at": datetime.now()
            })

            # Obtener el ID del carrito insertado
            result = db.execute(text("SELECT @@IDENTITY as cart_id"))
            cart_id_row = result.fetchone()
            cart_id = int(cart_id_row[0]) if cart_id_row and cart_id_row[0] else None

        # Verificar si el producto ya está en el carrito
        existing_item_result = db.execute(text("""
            SELECT id, cantidad FROM ecomerce_carrito_items
            WHERE id_carrito = :cart_id AND id_producto = :product_id
        """), {"cart_id": cart_id, "product_id": product_id})

        existing_items = existing_item_result.fetchall()

        if existing_items:
            # Actualizar cantidad existente
            existing_item = existing_items[0]
            new_quantity = existing_item[1] + quantity
            db.execute(text("""
                UPDATE ecomerce_carrito_items
                SET cantidad = :cantidad
                WHERE id = :item_id
            """), {
                "item_id": existing_item[0],
                "cantidad": new_quantity
            })
        else:
            # Agregar nuevo item
            db.execute(text("""
                INSERT INTO ecomerce_carrito_items
                (id_carrito, id_producto, cantidad, precio_unitario)
                VALUES (:cart_id, :product_id, :cantidad, :precio)
            """), {
                "cart_id": cart_id,
                "product_id": product_id,
                "cantidad": quantity,
                "precio": price
            })

        db.commit()

        return {
            "message": "Producto agregado al carrito",
            "cart_id": cart_id,
            "product_id": product_id,
            "quantity": quantity
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error agregando producto al carrito: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/carrito_items/carrito/{cart_id}")
async def get_carrito_items(
    cart_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los items de un carrito específico
    """
    try:
        # Obtener usuario del token JWT
        user = get_current_ecommerce_user(credentials.credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")

        # Verificar que el carrito pertenece al usuario
        cart_check = db.execute(text("""
            SELECT id_usuario FROM ecomerce_carritos
            WHERE id = :cart_id
        """), {"cart_id": cart_id}).fetchall()

        if not cart_check or cart_check[0][0] != user['id']:
            raise HTTPException(status_code=403, detail="No autorizado para acceder a este carrito")

        # Obtener items del carrito
        result = db.execute(text("""
            SELECT
                ci.id,
                ci.id_carrito,
                ci.id_producto,
                ci.cantidad,
                ci.precio_unitario,
                p.nombre as product_name,
                p.imagen_url as product_image,
                p.codigo as product_codigo
            FROM ecomerce_carrito_items ci
            LEFT JOIN ecomerce_productos p ON ci.id_producto = p.id
            WHERE ci.id_carrito = :cart_id
            ORDER BY ci.id
        """), {"cart_id": cart_id})

        items = []
        for row in result:
            item = {
                "id": row[0],
                "id_carrito": row[1],
                "id_producto": row[2],
                "cantidad": row[3],
                "precio_unitario": row[4],
                "variant_data": None,
                "created_at": None,
                "updated_at": None,
                "product_name": row[5] or f"Producto {row[2]}",
                "product_image": row[6] or "/static/img/logo.png",
                "product_codigo": row[7] or ""
            }
            items.append(item)

        return items

    except Exception as e:
        logger.error(f"Error obteniendo items del carrito {cart_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/carrito_items/id/{item_id}")
def update_carrito_item(
    item_id: int,
    cart_update: UpdateCartItemRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Actualiza la cantidad de un item del carrito
    """
    try:
        # Obtener usuario del token JWT
        user = get_current_ecommerce_user(credentials.credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")

        cantidad = cart_update.cantidad

        # Verificar que el item pertenece al usuario
        item_check = db.execute(text("""
            SELECT c.id_usuario FROM ecomerce_carrito_items ci
            JOIN ecomerce_carritos c ON ci.id_carrito = c.id
            WHERE ci.id = :item_id
        """), {"item_id": item_id}).fetchall()

        if not item_check or item_check[0][0] != user['id']:
            raise HTTPException(status_code=403, detail="No autorizado para modificar este item")

        if cantidad <= 0:
            # Si cantidad es 0 o negativa, eliminar el item
            db.execute(text("""
                DELETE FROM ecomerce_carrito_items
                WHERE id = :item_id
            """), {"item_id": item_id})
            db.commit()
            return {"message": "Item eliminado"}

        # Actualizar cantidad
        result = db.execute(text("""
            UPDATE ecomerce_carrito_items
            SET cantidad = :cantidad
            WHERE id = :item_id
        """), {
            "item_id": item_id,
            "cantidad": cantidad
        })

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item no encontrado")

        db.commit()
        return {"message": "Item actualizado"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/carrito_items/id/{item_id}")
async def delete_carrito_item(
    item_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Elimina un item del carrito
    """
    try:
        # Obtener usuario del token JWT
        user = get_current_ecommerce_user(credentials.credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")

        # Verificar que el item pertenece al usuario
        item_check = db.execute(text("""
            SELECT c.id_usuario FROM ecomerce_carrito_items ci
            JOIN ecomerce_carritos c ON ci.id_carrito = c.id
            WHERE ci.id = :item_id
        """), {"item_id": item_id}).fetchall()

        if not item_check or item_check[0][0] != user['id']:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este item")

        result = db.execute(text("""
            DELETE FROM ecomerce_carrito_items
            WHERE id = :item_id
        """), {"item_id": item_id})

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item no encontrado")

        db.commit()
        return {"message": "Item eliminado"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/carritos/activo/{user_id}")
async def get_carrito_activo(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Obtiene el carrito activo de un usuario, o crea uno si no existe
    """
    try:
        # Obtener usuario del token JWT
        user = get_current_ecommerce_user(credentials.credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")

        # Verificar que el user_id del token coincide con el solicitado
        if user['id'] != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para acceder a este carrito")

        # Buscar carrito activo del usuario
        result = db.execute(text("""
            SELECT TOP 1 id, id_usuario, estado, created_at
            FROM ecomerce_carritos
            WHERE id_usuario = :user_id AND estado = 'activo'
            ORDER BY created_at DESC
        """), {"user_id": user_id})

        cart = result.fetchone()

        if cart:
            # Carrito activo encontrado
            return {
                "id": cart[0],
                "id_usuario": cart[1],
                "estado": cart[2],
                "created_at": cart[3].isoformat() if cart[3] else None,
                "updated_at": None
            }
        else:
            # No hay carrito activo, crear uno nuevo
            logger.info(f"Creando carrito activo para usuario {user_id}")
            try:
                # Insertar carrito
                logger.info(f"Ejecutando INSERT para usuario {user_id}")
                db.execute(text("""
                    INSERT INTO ecomerce_carritos (id_usuario, estado, created_at)
                    VALUES (:user_id, 'activo', :created_at)
                """), {
                    "user_id": user_id,
                    "created_at": datetime.now()
                })
                logger.info(f"INSERT ejecutado exitosamente para usuario {user_id}")

                # Obtener el ID del carrito insertado usando @@IDENTITY
                logger.info("Ejecutando @@IDENTITY()")
                result = db.execute(text("SELECT @@IDENTITY as cart_id"))
                cart_id_row = result.fetchone()
                logger.info(f"Resultado de @@IDENTITY: {cart_id_row}")

                if cart_id_row and cart_id_row[0]:
                    cart_id = int(cart_id_row[0])
                    logger.info(f"Cart ID obtenido: {cart_id}")
                else:
                    logger.error("No se obtuvo ID del carrito insertado con @@IDENTITY")
                    raise Exception("No se pudo obtener el ID del carrito insertado")

                logger.info(f"Haciendo commit de la transacción para cart_id {cart_id}")
                db.commit()
                logger.info(f"Commit exitoso para cart_id {cart_id}")

                return {
                    "id": cart_id,
                    "id_usuario": user_id,
                    "estado": "activo",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            except Exception as insert_error:
                logger.error(f"Error creando carrito: {insert_error}")
                logger.error(f"Tipo de error: {type(insert_error)}")
                import traceback
                logger.error(f"Traceback completo: {traceback.format_exc()}")
                db.rollback()
                raise

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo carrito activo para usuario {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")