from fastapi import APIRouter, HTTPException, Depends, Body, Request
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
import logging
from datetime import datetime
from pydantic import BaseModel
import mercadopago
import os
import hashlib
import hmac

from db.database import get_db
from security.ecommerce_auth import get_current_ecommerce_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.pedidos import EcomercePedidos
from ..models.pedido_items import EcomercePedidoItems
from ..Controllers.pedidos import create_pedidos
from Services.mail.mail import enviar_correo_presupuesto
from config import MERCADOPAGO_PUBLIC_KEY

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Configuración de MercadoPago
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
MERCADOPAGO_WEBHOOK_SECRET = os.getenv("MERCADOPAGO_WEBHOOK_SECRET", "")
if MERCADOPAGO_ACCESS_TOKEN:
    sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
else:
    sdk = None
    logger.warning("MERCADOPAGO_ACCESS_TOKEN no configurado")

if not MERCADOPAGO_WEBHOOK_SECRET:
    logger.warning("MERCADOPAGO_WEBHOOK_SECRET no configurado - los webhooks no serán validados")

def validate_mercadopago_signature(x_signature: str, x_request_id: str, data_id: str) -> bool:
    """
    Valida la firma HMAC-SHA256 de MercadoPago según la documentación oficial.

    Args:
        x_signature: Header x-signature recibido (formato: ts=123456789,v1=abcdef...)
        x_request_id: Header x-request-id recibido
        data_id: ID del evento (data.id de la notificación)

    Returns:
        bool: True si la firma es válida, False en caso contrario
    """
    if not MERCADOPAGO_WEBHOOK_SECRET:
        logger.warning("No se puede validar firma - MERCADOPAGO_WEBHOOK_SECRET no configurado")
        return True  # Permitir webhooks sin validación si no hay clave secreta

    try:
        # Separar ts y v1 del header x-signature
        parts = x_signature.split(",")
        ts = None
        received_hash = None

        for part in parts:
            key_value = part.split("=", 1)
            if len(key_value) == 2:
                key, value = key_value
                key = key.strip()
                value = value.strip()
                if key == "ts":
                    ts = value
                elif key == "v1":
                    received_hash = value

        if not ts or not received_hash:
            logger.error(f"Header x-signature malformado: {x_signature}")
            return False

        # Crear el template: id:{data_id};request-id:{x_request_id};ts:{ts};
        manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

        # Generar HMAC-SHA256
        secret_bytes = MERCADOPAGO_WEBHOOK_SECRET.encode('utf-8')
        manifest_bytes = manifest.encode('utf-8')
        computed_hash = hmac.new(secret_bytes, manifest_bytes, hashlib.sha256).hexdigest()

        # Comparar hashes
        is_valid = hmac.compare_digest(computed_hash, received_hash)

        if is_valid:
            logger.info(f"Firma HMAC validada correctamente para data_id: {data_id}")
        else:
            logger.error(f"Firma HMAC inválida - Recibido: {received_hash}, Calculado: {computed_hash}")

        return is_valid

    except Exception as e:
        logger.error(f"Error validando firma HMAC: {e}")
        return False

# Modelo para la solicitud de checkout
class CheckoutRequest(BaseModel):
    payment_method: str  # 'efectivo', 'mercadopago', 'presupuesto'

@router.post("/")
async def checkout(
    checkout_data: CheckoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Procesa el checkout del carrito activo del usuario
    """
    logger.info("=== INICIANDO CHECKOUT ===")
    try:
        # Obtener usuario del token
        logger.info("Obteniendo usuario del token...")
        user = get_current_ecommerce_user(credentials.credentials, db)
        if not user:
            logger.error("Usuario no encontrado en token")
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")

        user_id = user.get('id')
        if not user_id:
            logger.error("Usuario sin ID válido")
            raise HTTPException(status_code=401, detail="Usuario no válido")
        
        logger.info(f"Usuario autenticado: ID={user_id}, Email={user.get('email')}")
        payment_method = checkout_data.payment_method
        logger.info(f"Método de pago: {payment_method}")

        # Validar método de pago
        if payment_method not in ['efectivo', 'mercadopago', 'presupuesto']:
            logger.error(f"Método de pago inválido: {payment_method}")
            raise HTTPException(status_code=400, detail="Método de pago no válido")

        # Obtener carrito activo del usuario
        logger.info(f"Buscando carrito activo para usuario {user_id}...")
        cart_result = db.execute(text("""
            SELECT TOP 1 id FROM ecomerce_carritos
            WHERE id_usuario = :user_id AND estado = 'activo'
            ORDER BY created_at DESC
        """), {"user_id": user_id})

        cart_row = cart_result.fetchone()
        if not cart_row:
            logger.error(f"No se encontró carrito activo para usuario {user_id}")
            raise HTTPException(status_code=400, detail="No hay carrito activo")

        cart_id = cart_row[0]
        logger.info(f"Carrito encontrado: ID={cart_id}")

        # Obtener items del carrito
        logger.info(f"Obteniendo items del carrito {cart_id}...")
        items_result = db.execute(text("""
            SELECT ci.id_producto, ci.cantidad, ci.precio_unitario, p.nombre
            FROM ecomerce_carrito_items ci
            JOIN ecomerce_productos p ON ci.id_producto = p.id
            WHERE ci.id_carrito = :cart_id
        """), {"cart_id": cart_id})

        cart_items = items_result.fetchall()
        if not cart_items:
            logger.error(f"Carrito {cart_id} está vacío")
            raise HTTPException(status_code=400, detail="El carrito está vacío")

        logger.info(f"Items encontrados: {len(cart_items)}")
        for item in cart_items:
            logger.info(f"  Item: Producto {item[0]}, Cantidad {item[1]}, Precio {item[2]}, Nombre {item[3]}")

        # Calcular total
        total = sum(item[1] * item[2] for item in cart_items)
        logger.info(f"Total calculado: {total}")

        # Procesar según método de pago
        if payment_method == 'efectivo':
            # Para pago en efectivo, crear el pedido y completarlo inmediatamente
            logger.info("Creando pedido para pago en efectivo...")
            pedido_data = {
                'id_usuario': user_id,
                'fecha_pedido': datetime.now(),
                'total': total,
                'estado': 'pendiente',
                'metodo_pago': payment_method
            }

            pedido = create_pedidos(db=db, pedidos=pedido_data, user_data=user, request=None)
            logger.info(f"Pedido creado: ID={pedido.id}")

            # Crear items del pedido
            logger.info("Creando items del pedido...")
            for item in cart_items:
                pedido_item = EcomercePedidoItems(
                    id_pedido=pedido.id,
                    id_producto=item[0],
                    cantidad=item[1],
                    precio_unitario=item[2],
                    nombre_producto=item[3] or f"Producto {item[0]}"
                )
                db.add(pedido_item)

            # Completar el pedido
            logger.info(f"Completando pedido {pedido.id} para pago en efectivo")
            db.execute(text("""
                UPDATE ecomerce_pedidos
                SET estado = 'confirmado'
                WHERE id = :pedido_id
            """), {"pedido_id": pedido.id})

            # Limpiar carrito (marcar como completado)
            logger.info(f"Marcando carrito {cart_id} como completado...")
            db.execute(text("""
                UPDATE ecomerce_carritos
                SET estado = 'completado'
                WHERE id = :cart_id
            """), {"cart_id": cart_id})

            db.commit()
            logger.info("Transacción committed exitosamente")

            return {
                "mensaje": "Pedido creado exitosamente. Pagarás en efectivo al recibir el pedido.",
                "pedido_id": pedido.id,
                "total": total,
                "metodo_pago": payment_method
            }

        elif payment_method == 'mercadopago':
            # Para MercadoPago, NO crear el pedido aún
            # Solo crear la preferencia de pago y esperar confirmación del webhook
            logger.info(f"Método MercadoPago seleccionado - creando preferencia sin pedido")

            if not sdk:
                logger.error("SDK de MercadoPago no inicializado")
                raise HTTPException(status_code=500, detail="MercadoPago no configurado")

            try:
                logger.info(f"Creando preferencia de pago para carrito {cart_id}, total: {total}")

                # Preparar items para la preferencia
                items_for_preference = []
                for item in cart_items:
                    items_for_preference.append({
                        "title": item[3] or f"Producto {item[0]}",  # nombre del producto
                        "quantity": int(item[1]),  # cantidad
                        "unit_price": float(item[2]),  # precio unitario
                    })

                # Crear preferencia de pago sin pedido
                # La external_reference será el ID del carrito
                preference_data = {
                    "items": items_for_preference,
                    "back_urls": {
                        "success": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/ecomerce/checkout/success",
                        "failure": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/ecomerce/checkout/failure",
                        "pending": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/ecomerce/checkout/pending"
                    },
                    "external_reference": f"CART-{cart_id}",  # Usar ID del carrito en lugar del pedido
                    "notification_url": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/ecomerce/checkout/webhook/mercadopago",
                    "metadata": {
                        "cart_id": cart_id,
                        "user_id": user_id
                    }
                }

                logger.info(f"Datos de preferencia: {preference_data}")

                preference_response = sdk.preference().create(preference_data)
                logger.info(f"Respuesta de MercadoPago: {preference_response}")

                preference = preference_response["response"]

                logger.info(f"Preferencia creada: {preference['id']} para carrito {cart_id}")

                # NO crear pedido ni marcar carrito como completado
                # Eso se hará cuando el webhook confirme el pago

                return {
                    "mensaje": "Preferencia de pago creada. Completa el pago con MercadoPago para confirmar tu pedido.",
                    "cart_id": cart_id,
                    "total": total,
                    "metodo_pago": payment_method,
                    "preference_id": preference["id"]
                }

            except KeyError as e:
                logger.error(f"Error accediendo a respuesta de MercadoPago: {e}")
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Error en respuesta de MercadoPago: {str(e)}")
            except Exception as e:
                logger.error(f"Error creando preferencia MercadoPago: {e}")
                logger.error(f"Type: {type(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Error al procesar pago con MercadoPago: {str(e)}")

        elif payment_method == 'presupuesto':
            # Para presupuesto, crear el pedido inmediatamente
            logger.info("Creando pedido para presupuesto...")
            pedido_data = {
                'id_usuario': user_id,
                'fecha_pedido': datetime.now(),
                'total': total,
                'estado': 'pendiente',
                'metodo_pago': payment_method
            }

            pedido = create_pedidos(db=db, pedidos=pedido_data, user_data=user, request=None)
            logger.info(f"Pedido creado: ID={pedido.id}")

            # Crear items del pedido
            logger.info("Creando items del pedido...")
            for item in cart_items:
                pedido_item = EcomercePedidoItems(
                    id_pedido=pedido.id,
                    id_producto=item[0],
                    cantidad=item[1],
                    precio_unitario=item[2],
                    nombre_producto=item[3] or f"Producto {item[0]}"
                )
                db.add(pedido_item)

            # Completar el pedido
            logger.info(f"Completando pedido {pedido.id} para presupuesto")
            db.execute(text("""
                UPDATE ecomerce_pedidos
                SET estado = 'presupuesto_solicitado'
                WHERE id = :pedido_id
            """), {"pedido_id": pedido.id})

            # Limpiar carrito (marcar como completado)
            logger.info(f"Marcando carrito {cart_id} como completado...")
            db.execute(text("""
                UPDATE ecomerce_carritos
                SET estado = 'completado'
                WHERE id = :cart_id
            """), {"cart_id": cart_id})

            db.commit()
            logger.info("Transacción committed exitosamente")

            # Enviar presupuesto por email
            try:
                logger.info(f"Iniciando proceso de presupuesto para usuario {user_id}")
                logger.info(f"Usuario completo: {user}")

                # Obtener email del usuario
                logger.info(f"Consultando email para user_id: {user_id}")
                user_email_result = db.execute(text("""
                    SELECT email FROM ecomerce_usuarios WHERE id = :user_id
                """), {"user_id": user_id})
                user_email_row = user_email_result.fetchone()
                user_email = user_email_row[0] if user_email_row else None

                logger.info(f"Email del usuario: {user_email}")
                logger.info(f"Resultado de la consulta: {user_email_row}")

                email_sent = False
                if user_email:
                    logger.info("Preparando detalles del presupuesto")
                    # Preparar detalles del presupuesto
                    presupuesto_detalles = {
                        'pedido_id': pedido.id,
                        'usuario': user.get('nombre', 'Usuario'),
                        'email': user_email,
                        'total': total,
                        'items': [
                            {
                                'nombre': item[3] or f"Producto {item[0]}",
                                'cantidad': item[1],
                                'precio_unitario': item[2],
                                'subtotal': item[1] * item[2]
                            } for item in cart_items
                        ]
                    }

                    logger.info(f"Detalles del presupuesto preparados: {presupuesto_detalles}")

                    # Enviar email (implementar esta función)
                    logger.info("Llamando a enviar_correo_presupuesto")
                    await enviar_correo_presupuesto(presupuesto_detalles)
                    logger.info("Email de presupuesto enviado exitosamente")
                    email_sent = True
                else:
                    logger.warning(f"No se encontró email para usuario {user_id}, no se enviará presupuesto")

                mensaje = "Presupuesto enviado exitosamente. Revisa tu email." if email_sent else "Pedido creado exitosamente. No se pudo enviar el presupuesto por email (email no configurado)."

                return {
                    "mensaje": mensaje,
                    "pedido_id": pedido.id,
                    "total": total,
                    "metodo_pago": payment_method
                }
            except Exception as e:
                logger.error(f"Error enviando presupuesto: {e}")
                logger.error(f"Traceback completo: {e.__traceback__}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # No lanzar excepción, completar el pedido pero informar del error
                return {
                    "mensaje": "Pedido creado exitosamente, pero hubo un error enviando el presupuesto por email. Contacta al soporte.",
                    "pedido_id": pedido.id,
                    "total": total,
                    "metodo_pago": payment_method
                }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en checkout: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# TODO: Implementar webhooks de MercadoPago
@router.post("/webhook/mercadopago")
async def mercadopago_webhook(
    request: Request,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Webhook para recibir notificaciones de MercadoPago con validación de firma HMAC-SHA256
    """
    try:
        logger.info(f"Webhook MercadoPago recibido: {data}")

        # Extraer headers necesarios para validación
        x_signature = request.headers.get("x-signature")
        x_request_id = request.headers.get("x-request-id")

        # Verificar que sea una notificación válida
        if "type" not in data or data["type"] != "payment":
            logger.info("Notificación ignorada - no es de tipo 'payment'")
            return {"status": "ignored"}

        payment_data = data.get("data", {})
        payment_id = payment_data.get("id")

        if not payment_id:
            logger.error("Payment ID faltante en notificación")
            return {"status": "error", "message": "Payment ID missing"}

        # Validar firma HMAC si está configurada
        if x_signature and x_request_id:
            is_valid_signature = validate_mercadopago_signature(x_signature, x_request_id, str(payment_id))
            if not is_valid_signature:
                logger.error("Firma HMAC inválida - notificación rechazada")
                return {"status": "error", "message": "Invalid signature"}

        # Obtener detalles del pago desde MercadoPago
        if sdk:
            try:
                payment_info = sdk.payment().get(payment_id)
                payment = payment_info["response"]

                # Extraer información relevante
                status = payment.get("status")
                status_detail = payment.get("status_detail")
                external_reference = payment.get("external_reference")
                payment_method_id = payment.get("payment_method_id")
                transaction_amount = payment.get("transaction_amount")

                logger.info(f"Pago {payment_id}: status={status}, external_reference={external_reference}")

                if external_reference:
                    # La external_reference ahora es CART-{cart_id}
                    if not external_reference.startswith("CART-"):
                        logger.warning(f"External reference inválida: {external_reference}")
                        return {"status": "error", "message": "Invalid external reference format"}

                    cart_id = int(external_reference.replace("CART-", ""))
                    logger.info(f"Procesando pago para carrito {cart_id}")

                    # Verificar que el carrito existe y está activo
                    cart_check = db.execute(text("""
                        SELECT id, id_usuario FROM ecomerce_carritos WHERE id = :cart_id AND estado = 'activo'
                    """), {"cart_id": cart_id}).fetchone()

                    if not cart_check:
                        logger.error(f"Carrito {cart_id} no encontrado o no está activo")
                        return {"status": "error", "message": "Cart not found or already processed"}

                    user_id = cart_check[1]

                    # Solo crear el pedido si el pago fue APROBADO
                    if status == "approved":
                        logger.info(f"✅ Pago aprobado - creando pedido para carrito {cart_id}")

                        # Obtener items del carrito
                        cart_items_result = db.execute(text("""
                            SELECT ci.id_producto, ci.cantidad, ci.precio_unitario, p.nombre
                            FROM ecomerce_carrito_items ci
                            JOIN ecomerce_productos p ON ci.id_producto = p.id
                            WHERE ci.id_carrito = :cart_id
                        """), {"cart_id": cart_id})

                        cart_items = cart_items_result.fetchall()

                        if not cart_items:
                            logger.error(f"Carrito {cart_id} no tiene items")
                            return {"status": "error", "message": "Cart is empty"}

                        # Calcular total
                        total = sum(item[1] * item[2] for item in cart_items)

                        # Obtener datos del usuario
                        user_result = db.execute(text("""
                            SELECT id, email, nombre FROM ecomerce_usuarios WHERE id = :user_id
                        """), {"user_id": user_id}).fetchone()

                        if not user_result:
                            logger.error(f"Usuario {user_id} no encontrado")
                            return {"status": "error", "message": "User not found"}

                        user_data = {
                            'id': user_result[0],
                            'email': user_result[1],
                            'nombre': user_result[2]
                        }

                        # Crear el pedido
                        pedido_data = {
                            'id_usuario': user_id,
                            'fecha_pedido': datetime.now(),
                            'total': total,
                            'estado': 'pagado',  # Estado directamente pagado
                            'metodo_pago': 'mercadopago',
                            'payment_status': status,
                            'payment_method_id': payment_method_id,
                            'transaction_amount': transaction_amount
                        }

                        pedido = create_pedidos(db=db, pedidos=pedido_data, user_data=user_data, request=None)
                        logger.info(f"✅ Pedido creado: ID={pedido.id}")

                        # Crear items del pedido
                        for item in cart_items:
                            pedido_item = EcomercePedidoItems(
                                id_pedido=pedido.id,
                                id_producto=item[0],
                                cantidad=item[1],
                                precio_unitario=item[2],
                                nombre_producto=item[3] or f"Producto {item[0]}"
                            )
                            db.add(pedido_item)

                        # Marcar carrito como completado
                        db.execute(text("""
                            UPDATE ecomerce_carritos
                            SET estado = 'completado', updated_at = :updated_at
                            WHERE id = :cart_id
                        """), {
                            "updated_at": datetime.now(),
                            "cart_id": cart_id
                        })

                        db.commit()
                        logger.info(f"✅ Pedido {pedido.id} creado y carrito {cart_id} completado tras pago aprobado")

                    elif status == "pending":
                        logger.info(f"⏳ Pago pendiente ({status_detail}) - NO se crea pedido aún")
                        # No crear pedido, solo registrar que el pago está pendiente
                    elif status == "rejected":
                        logger.warning(f"❌ Pago rechazado ({status_detail}) - NO se crea pedido")
                        # No crear pedido
                    elif status == "cancelled":
                        logger.warning(f"❌ Pago cancelado - NO se crea pedido")
                        # No crear pedido
                    else:
                        logger.warning(f"⚠️ Status desconocido '{status}' - NO se crea pedido")

                    # Aquí se podrían agregar notificaciones por email al usuario
                    # sobre el cambio de estado del pedido

                else:
                    logger.warning(f"Pago {payment_id} sin external_reference")

            except Exception as e:
                logger.error(f"Error obteniendo detalles del pago {payment_id}: {e}")
                return {"status": "error", "message": f"Error getting payment details: {str(e)}"}

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error procesando webhook MercadoPago: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

# Endpoints de redirección para MercadoPago
@router.get("/success")
async def mercadopago_success(
    payment_id: str = None,
    status: str = None,
    external_reference: str = None,
    merchant_order_id: str = None
):
    """
    Página de redirección cuando el pago con MercadoPago es exitoso
    """
    logger.info(f"Redirección success MercadoPago: payment_id={payment_id}, status={status}, external_reference={external_reference}")
    
    # Servir el archivo HTML estático
    return FileResponse(
        path="static/checkout-success.html",
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.get("/failure")
async def mercadopago_failure(
    payment_id: str = None,
    status: str = None,
    external_reference: str = None,
    merchant_order_id: str = None
):
    """
    Página de redirección cuando el pago con MercadoPago falla
    """
    logger.warning(f"Redirección failure MercadoPago: payment_id={payment_id}, status={status}, external_reference={external_reference}")
    
    # Servir el archivo HTML estático
    return FileResponse(
        path="static/checkout-failure.html",
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.get("/config/mercadopago")
async def get_mercadopago_config():
    """
    Endpoint para obtener la configuración de MercadoPago para el frontend
    """
    return {
        "public_key": MERCADOPAGO_PUBLIC_KEY,
        "is_configured": bool(MERCADOPAGO_PUBLIC_KEY and MERCADOPAGO_ACCESS_TOKEN)
    }

@router.get("/pending")
async def mercadopago_pending(
    payment_id: str = None,
    status: str = None,
    external_reference: str = None,
    merchant_order_id: str = None
):
    """
    Página de redirección cuando el pago con MercadoPago está pendiente
    """
    logger.info(f"Redirección pending MercadoPago: payment_id={payment_id}, status={status}, external_reference={external_reference}")
    
    # Servir el archivo HTML estático
    return FileResponse(
        path="static/checkout-pending.html",
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )