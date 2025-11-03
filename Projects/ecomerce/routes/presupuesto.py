from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from datetime import datetime

from db.database import get_db
from Projects.ecomerce.models.presupuesto import Presupuesto
from Projects.ecomerce.schemas.presupuesto import PresupuestoRequest, PresupuestoResponse
from Services.mail.mail import enviar_multiples_emails

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Cargando router de presupuesto...")

router = APIRouter()

@router.post("/presupuesto", response_model=PresupuestoResponse)
async def crear_solicitud_presupuesto(
    request: PresupuestoRequest,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva solicitud de presupuesto
    """
    try:
        # Validar datos básicos
        if not request.nombre.strip():
            raise HTTPException(status_code=400, detail="El nombre es obligatorio")

        if not request.mensaje.strip():
            raise HTTPException(status_code=400, detail="El mensaje es obligatorio")

        # Crear nueva solicitud de presupuesto
        nueva_solicitud = Presupuesto(
            nombre=request.nombre.strip(),
            email=request.email,
            telefono=request.telefono.strip(),
            mensaje=request.mensaje.strip(),
            estado="pendiente",
            fecha_creacion=datetime.utcnow()
        )

        db.add(nueva_solicitud)
        db.commit()
        db.refresh(nueva_solicitud)

        logger.info(f"Nueva solicitud de presupuesto creada: {nueva_solicitud.id} - {nueva_solicitud.nombre}")

        # Enviar email de notificación
        try:
            # Preparar contenido del email para el administrador
            asunto_admin = f"Nueva solicitud de presupuesto - {nueva_solicitud.nombre}"

            mensaje_admin = f"""
Nueva solicitud de presupuesto recibida:

ID de Solicitud: {nueva_solicitud.id}
Fecha: {nueva_solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

Datos del cliente:
- Nombre: {nueva_solicitud.nombre}
- Email: {nueva_solicitud.email}
- Teléfono: {nueva_solicitud.telefono}

Mensaje del cliente:
{nueva_solicitud.mensaje}

Estado actual: {nueva_solicitud.estado}

Por favor, revisa esta solicitud en el panel de administración.
"""

            # Preparar contenido del email de confirmación para el cliente
            asunto_cliente = "Confirmación de solicitud de presupuesto - Tienda Online"

            mensaje_cliente = f"""
¡Hola {nueva_solicitud.nombre}!

Hemos recibido tu solicitud de presupuesto correctamente.

Detalles de tu solicitud:
- ID de Solicitud: {nueva_solicitud.id}
- Fecha de recepción: {nueva_solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

Tu mensaje:
{nueva_solicitud.mensaje}

Nos pondremos en contacto contigo lo antes posible, generalmente dentro de 24 horas hábiles.

Si tienes alguna pregunta adicional, puedes responder a este email.

¡Gracias por confiar en nosotros!

Atentamente,
El equipo de Tienda Online
"""

            # Enviar emails de forma optimizada (concurrente)
            try:
                # Preparar lista de emails para envío concurrente
                emails_a_enviar = []

                # Email para el administrador
                from dotenv import load_dotenv
                import os
                load_dotenv()
                admin_email = os.getenv('USERNAME_EMAIL')

                if admin_email:
                    emails_a_enviar.append({
                        'destinatario': admin_email,
                        'asunto': f"Nueva solicitud de presupuesto - {nueva_solicitud.nombre}",
                        'mensaje': f"""
Nueva solicitud de presupuesto recibida:

ID de Solicitud: {nueva_solicitud.id}
Fecha: {nueva_solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

Datos del cliente:
- Nombre: {nueva_solicitud.nombre}
- Email: {nueva_solicitud.email}
- Teléfono: {nueva_solicitud.telefono}

Mensaje del cliente:
{nueva_solicitud.mensaje}

Estado actual: {nueva_solicitud.estado}

Por favor, revisa esta solicitud en el panel de administración.
"""
                    })

                # Email de confirmación para el cliente
                emails_a_enviar.append({
                    'destinatario': nueva_solicitud.email,
                    'asunto': "Confirmación de solicitud de presupuesto - Tienda Online",
                    'mensaje': f"""
¡Hola {nueva_solicitud.nombre}!

Hemos recibido tu solicitud de presupuesto correctamente.

Detalles de tu solicitud:
- ID de Solicitud: {nueva_solicitud.id}
- Fecha de recepción: {nueva_solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

Tu mensaje:
{nueva_solicitud.mensaje}

Nos pondremos en contacto contigo lo antes posible, generalmente dentro de 24 horas hábiles.

Si tienes alguna pregunta adicional, puedes responder a este email.

¡Gracias por confiar en nosotros!

Atentamente,
El equipo de Tienda Online
"""
                })

                # Enviar emails de forma concurrente
                resultado_envio = await enviar_multiples_emails(emails_a_enviar)

                if resultado_envio['success']:
                    logger.info(f"Emails enviados exitosamente: {resultado_envio['enviados']}/{resultado_envio['total']} en {resultado_envio['tiempo_total']:.2f}s")
                    if admin_email:
                        logger.info(f"Email de notificación enviado al administrador para presupuesto {nueva_solicitud.id}")
                    logger.info(f"Email de confirmación enviado al cliente {nueva_solicitud.email} para presupuesto {nueva_solicitud.id}")
                else:
                    logger.warning(f"Algunos emails fallaron: {resultado_envio['errores']} errores de {resultado_envio['total']}")

            except Exception as email_error:
                logger.error(f"Error al enviar emails de notificación: {str(email_error)}")
                # No fallar la solicitud si los emails fallan

        except Exception as email_error:
            logger.error(f"Error al enviar emails de notificación: {str(email_error)}")
            # No fallar la solicitud si los emails fallan

        return nueva_solicitud

    except Exception as e:
        logger.error(f"Error al crear solicitud de presupuesto: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/presupuesto")
async def obtener_solicitudes_presupuesto(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las solicitudes de presupuesto (para admin)
    """
    try:
        logger.info("Obteniendo solicitudes de presupuesto...")
        solicitudes = db.query(Presupuesto).offset(skip).limit(limit).all()
        logger.info(f"Se encontraron {len(solicitudes)} solicitudes de presupuesto")

        # Convertir a dict para evitar problemas con Pydantic
        result = []
        for solicitud in solicitudes:
            result.append({
                "id": solicitud.id,
                "nombre": solicitud.nombre,
                "email": solicitud.email,
                "telefono": solicitud.telefono,
                "mensaje": solicitud.mensaje,
                "fecha_creacion": solicitud.fecha_creacion.isoformat() if solicitud.fecha_creacion else None,
                "estado": solicitud.estado
            })

        return result

    except Exception as e:
        logger.error(f"Error al obtener solicitudes de presupuesto: {str(e)}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/presupuesto/{presupuesto_id}/estado")
async def actualizar_estado_presupuesto(
    presupuesto_id: int,
    estado: str,
    db: Session = Depends(get_db)
):
    """
    Actualizar el estado de una solicitud de presupuesto (para admin)
    """
    try:
        # Validar estado
        estados_validos = ["pendiente", "contactado", "aprobado", "rechazado"]
        if estado not in estados_validos:
            raise HTTPException(status_code=400, detail=f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}")

        # Buscar la solicitud
        solicitud = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud de presupuesto no encontrada")

        # Actualizar estado
        solicitud.estado = estado
        db.commit()

        logger.info(f"Estado de solicitud {presupuesto_id} actualizado a: {estado}")

        return {"message": "Estado actualizado exitosamente", "estado": estado}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar estado de presupuesto: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")