from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.usuarios import EcomerceUsuarios as Usuarios
from ..models.pedidos import EcomercePedidos
from ..models.carritos import EcomerceCarritos
from ..models.carrito_items import EcomerceCarrito_items
from ..models.presupuesto import Presupuesto
from ..models.productos import EcomerceProductos
from db.models.logs.activity_log import ActivityLog
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def log_activity(db: Session, user_id: int, action: str, description: str, request: Request):
    """
    Función auxiliar para registrar actividades del usuario en la tabla activity_log.
    Esta función está comentada por defecto y puede activarse según sea necesario.
    """
    # try:
    #     # Obtener IP del cliente
    #     client_ip = request.client.host if request.client else "unknown"
    #     
    #     # Obtener User-Agent
    #     user_agent = request.headers.get("user-agent", "unknown")
    #     
    #     # Crear registro de actividad
    #     activity = ActivityLog(
    #         usuario_id=user_id,
    #         accion=action,
    #         descripcion=description,
    #         ip_address=client_ip,
    #         user_agent=user_agent
    #     )
    #     
    #     db.add(activity)
    #     db.commit()
    #     
    # except Exception as e:
    #     logger.error(f"Error al registrar actividad: {e}")
    #     db.rollback()  # No fallar la operación principal por error de logging

def create_usuarios(db: Session, usuarios, user_data: dict = None, request: Request = None) -> Usuarios:
    """
    Crea un nuevo registro de Usuarios en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos (excluyendo PK autoincrement si aplica)
        if isinstance(usuarios, dict):
            usuarios_data = usuarios
        else:
            usuarios_data = {}
            for field in ['nombre', 'apellido', 'email', 'contraseña_hash', 'telefono', 'direccion', 'google_maps_link', 'ciudad', 'provincia', 'pais', 'created_at', 'active']:
                if hasattr(usuarios, field):
                    usuarios_data[field] = getattr(usuarios, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_usuarios (nombre, apellido, email, contraseña_hash, telefono, direccion, google_maps_link, ciudad, provincia, pais, created_at, active)
            OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.apellido, INSERTED.email, INSERTED.contraseña_hash, INSERTED.telefono, INSERTED.direccion, INSERTED.google_maps_link, INSERTED.ciudad, INSERTED.provincia, INSERTED.pais, INSERTED.created_at, INSERTED.active
            VALUES (:nombre, :apellido, :email, :contraseña_hash, :telefono, :direccion, :google_maps_link, :ciudad, :provincia, :pais, :created_at, :active)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, usuarios_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Usuarios con los valores devueltos
        new_usuarios = Usuarios()
        new_usuarios.id = row[0]
        new_usuarios.nombre = row[1]
        new_usuarios.apellido = row[2]
        new_usuarios.email = row[3]
        new_usuarios.contraseña_hash = row[4]
        new_usuarios.telefono = row[5]
        new_usuarios.direccion = row[6]
        new_usuarios.google_maps_link = row[7]
        new_usuarios.ciudad = row[8]
        new_usuarios.provincia = row[9]
        new_usuarios.pais = row[10]
        new_usuarios.created_at = row[11]
        new_usuarios.active = row[12]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Usuarios (ID: {new_usuarios.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_usuarios
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Usuarios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_usuarios(db: Session, id: int) -> Optional[Usuarios]:
    """
    Obtiene un registro de Usuarios por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, nombre, apellido, email, contraseña_hash, telefono, direccion, google_maps_link, ciudad, provincia, pais, created_at, active FROM ecomerce_usuarios WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuarios no encontrado.")
        
        # Crear el objeto directamente con los valores
        usuarios = Usuarios()
        usuarios.id = result[0]
        usuarios.nombre = result[1]
        usuarios.apellido = result[2]
        usuarios.email = result[3]
        usuarios.contraseña_hash = result[4]
        usuarios.telefono = result[5]
        usuarios.direccion = result[6]
        usuarios.google_maps_link = result[7]
        usuarios.ciudad = result[8]
        usuarios.provincia = result[9]
        usuarios.pais = result[10]
        usuarios.created_at = result[11]
        usuarios.active = result[12]
        
        return usuarios
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_usuarios(db: Session) -> List[Usuarios]:
    """
    Obtiene una lista de todos los registros de Usuarios usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, nombre, apellido, email, contraseña_hash, telefono, direccion, google_maps_link, ciudad, provincia, pais, created_at, active FROM ecomerce_usuarios")
        )
        
        usuarioss = []
        for row in result.fetchall():
            usuarios = Usuarios()
            usuarios.id = row[0]
            usuarios.nombre = row[1]
            usuarios.apellido = row[2]
            usuarios.email = row[3]
            usuarios.contraseña_hash = row[4]
            usuarios.telefono = row[5]
            usuarios.direccion = row[6]
            usuarios.google_maps_link = row[7]
            usuarios.ciudad = row[8]
            usuarios.provincia = row[9]
            usuarios.pais = row[10]
            usuarios.created_at = row[11]
            usuarios.active = row[12]
            usuarioss.append(usuarios)
        
        return usuarioss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_usuarios(db: Session, id: int, user_data: dict = None, request: Request = None) -> Usuarios:
    """
    Elimina un registro de Usuarios por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_usuarios 
                OUTPUT DELETED.id, DELETED.nombre, DELETED.apellido, DELETED.email, DELETED.contraseña_hash, DELETED.telefono, DELETED.direccion, DELETED.google_maps_link, DELETED.ciudad, DELETED.provincia, DELETED.pais, DELETED.created_at, DELETED.active
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuarios no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_usuarios = Usuarios()
        deleted_usuarios.id = result[0]
        deleted_usuarios.nombre = result[1]
        deleted_usuarios.apellido = result[2]
        deleted_usuarios.email = result[3]
        deleted_usuarios.contraseña_hash = result[4]
        deleted_usuarios.telefono = result[5]
        deleted_usuarios.direccion = result[6]
        deleted_usuarios.google_maps_link = result[7]
        deleted_usuarios.ciudad = result[8]
        deleted_usuarios.provincia = result[9]
        deleted_usuarios.pais = result[10]
        deleted_usuarios.created_at = result[11]
        deleted_usuarios.active = result[12]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Usuarios (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_usuarios
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_usuarios(db: Session, id: int, usuarios_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Usuarios:
    """
    Actualiza un registro de Usuarios por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Usuarios con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_usuarios WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuarios no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        usuarios_data_copy = usuarios_data.copy()
        if 'id' in usuarios_data_copy:
            del usuarios_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not usuarios_data_copy:
            return get_usuarios(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in usuarios_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_usuarios
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.apellido, INSERTED.email, INSERTED.contraseña_hash, INSERTED.telefono, INSERTED.direccion, INSERTED.google_maps_link, INSERTED.ciudad, INSERTED.provincia, INSERTED.pais, INSERTED.created_at, INSERTED.active
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = usuarios_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Usuarios.")
        
        # Crear el objeto con los datos actualizados
        updated_usuarios = Usuarios()
        updated_usuarios.id = result[0]
        updated_usuarios.nombre = result[1]
        updated_usuarios.apellido = result[2]
        updated_usuarios.email = result[3]
        updated_usuarios.contraseña_hash = result[4]
        updated_usuarios.telefono = result[5]
        updated_usuarios.direccion = result[6]
        updated_usuarios.google_maps_link = result[7]
        updated_usuarios.ciudad = result[8]
        updated_usuarios.provincia = result[9]
        updated_usuarios.pais = result[10]
        updated_usuarios.created_at = result[11]
        updated_usuarios.active = result[12]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Usuarios (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return updated_usuarios
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Usuarios: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")

def get_user_profile(db: Session, user_email: str) -> dict:
    """
    Obtiene el perfil completo del usuario por email.
    """
    try:
        # Obtener datos del usuario por email - usando solo las columnas base que sabemos que existen
        user = db.execute(
            text("""
                SELECT id, nombre, apellido, email, telefono, direccion, google_maps_link, ciudad, provincia, pais, 
                       created_at, active 
                FROM ecomerce_usuarios 
                WHERE email = :email
            """),
            {"email": user_email}
        ).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        # Crear diccionario con datos del usuario
        user_data = {
            "id": user[0],
            "nombre": user[1] if user[1] else "",
            "apellido": user[2] if user[2] else "",
            "email": user[3] if user[3] else "",
            "telefono": user[4] if user[4] else "",
            "direccion": user[5] if user[5] else "",
            "google_maps_link": user[6] if user[6] else "",
            "ciudad": user[7] if user[7] else "",
            "provincia": user[8] if user[8] else "",
            "pais": user[9] if user[9] else "",
            "created_at": user[10],
            "active": user[11] if user[11] is not None else False
        }

        user_id = user_data["id"]

        # Usar las funciones separadas para obtener datos relacionados
        try:
            orders = get_user_orders(db, user_id)
        except Exception as e:
            logger.warning(f"Error obteniendo pedidos: {e}")
            orders = []

        try:
            active_cart = get_user_active_cart(db, user_id)
        except Exception as e:
            logger.warning(f"Error obteniendo carrito: {e}")
            active_cart = None

        try:
            budgets = get_user_budgets(db, user_email)
        except Exception as e:
            logger.warning(f"Error obteniendo presupuestos: {e}")
            budgets = []

        return {
            "user": user_data,
            "orders": orders,
            "active_cart": active_cart,
            "budgets": budgets,
            "orders_count": len(orders),
            "budgets_count": len(budgets)
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error SQL obteniendo perfil del usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error obteniendo perfil: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al obtener el perfil del usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado: {str(e)}")

def change_user_password(db: Session, user_email: str, current_password: str, new_password: str) -> dict:
    """
    Cambia la contraseña del usuario verificando la contraseña actual.
    """
    try:
        from passlib.context import CryptContext

        # Configurar el contexto de hash de contraseñas
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Obtener el usuario por email
        user_result = db.execute(
            text("SELECT id, contraseña_hash FROM ecomerce_usuarios WHERE email = :email"),
            {"email": user_email}
        ).first()

        if not user_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        user_id = user_result[0]
        stored_hash = user_result[1]

        # Verificar la contraseña actual
        if not pwd_context.verify(current_password, stored_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña actual es incorrecta")

        # Hash de la nueva contraseña
        new_hash = pwd_context.hash(new_password)

        # Actualizar la contraseña en la base de datos
        db.execute(
            text("UPDATE ecomerce_usuarios SET contraseña_hash = :new_hash WHERE id = :user_id"),
            {"new_hash": new_hash, "user_id": user_id}
        )
        db.commit()

        return {"message": "Contraseña cambiada correctamente"}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error cambiando contraseña: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error cambiando contraseña: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado cambiando contraseña: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado: {str(e)}")

def get_user_orders(db: Session, user_id: int) -> list:
    """
    Obtiene los pedidos del usuario con detalles.
    """
    try:
        orders_result = db.execute(
            text("""
                SELECT p.id, p.fecha_pedido, p.total, p.estado,
                       COUNT(pi.id) as items_count
                FROM ecomerce_pedidos p
                LEFT JOIN ecomerce_pedido_items pi ON p.id = pi.id_pedido
                WHERE p.id_usuario = :user_id
                GROUP BY p.id, p.fecha_pedido, p.total, p.estado
                ORDER BY p.fecha_pedido DESC
            """),
            {"user_id": user_id}
        ).fetchall()

        orders = []
        for row in orders_result:
            orders.append({
                "id": row[0],
                "fecha": str(row[1]) if row[1] else None,  # Convertir fecha a string
                "total": float(row[2]) if row[2] else 0.0,
                "estado": row[3],
                "items": [{"count": row[4] or 0}]  # Simplificado para compatibilidad
            })

        return orders

    except SQLAlchemyError as e:
        logger.error(f"Error obteniendo pedidos del usuario: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error obteniendo pedidos: {str(e)}")

def get_user_active_cart(db: Session, user_id: int) -> dict:
    """
    Obtiene el carrito activo del usuario con items detallados.
    """
    try:
        # Obtener carrito activo - SQL Server compatible
        cart_result = db.execute(
            text("""
                SELECT TOP 1 c.id, c.estado, c.created_at
                FROM ecomerce_carritos c
                WHERE c.id_usuario = :user_id AND c.estado = 'activo'
                ORDER BY c.created_at DESC
            """),
            {"user_id": user_id}
        ).first()

        if not cart_result:
            return None

        cart_id = cart_result[0]

        # Obtener items del carrito con detalles de productos
        items_result = db.execute(
            text("""
                SELECT p.id, p.nombre, p.imagen_url, ci.cantidad, ci.precio_unitario
                FROM ecomerce_carrito_items ci
                JOIN ecomerce_productos p ON ci.id_producto = p.id
                WHERE ci.id_carrito = :cart_id
            """),
            {"cart_id": cart_id}
        ).fetchall()

        items = []
        total = 0
        for row in items_result:
            item_total = row[3] * row[4]  # cantidad * precio_unitario
            total += item_total
            items.append({
                "producto": {
                    "id": row[0],
                    "nombre": row[1],
                    "imagen_url": row[2] or "/static/images/placeholder.png"
                },
                "cantidad": row[3],
                "precio_unitario": row[4],
                "total": item_total
            })

        return {
            "id": cart_id,
            "estado": cart_result[1],
            "created_at": cart_result[2],
            "items": items,
            "total": total
        }

    except Exception as e:
        logger.error(f"Error obteniendo carrito activo: {e}")
        db.rollback()  # Asegurar rollback en caso de error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error obteniendo carrito: {str(e)}")

def get_user_budgets(db: Session, user_email: str) -> list:
    """
    Obtiene los presupuestos del usuario.
    """
    try:
        budgets_result = db.execute(
            text("""
                SELECT id, nombre, email, telefono, mensaje, estado, fecha_creacion
                FROM presupuestos
                WHERE email = :email
                ORDER BY fecha_creacion DESC
            """),
            {"email": user_email}
        ).fetchall()

        budgets = []
        for row in budgets_result:
            budgets.append({
                "id": row[0],
                "nombre": row[1],
                "email": row[2],
                "telefono": row[3],
                "mensaje": row[4],
                "estado": row[5],
                "fecha": str(row[6]) if row[6] else None  # Convertir fecha a string
            })

        return budgets

    except SQLAlchemyError as e:
        logger.error(f"Error obteniendo presupuestos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error obteniendo presupuestos: {str(e)}")

def get_order_details(db: Session, order_id: int, user_id: int) -> dict:
    """
    Obtiene los detalles completos de un pedido específico del usuario.
    """
    try:
        # Verificar que el pedido pertenece al usuario
        order_result = db.execute(
            text("""
                SELECT p.id, p.fecha_pedido, p.total, p.estado, p.metodo_pago
                FROM ecomerce_pedidos p
                WHERE p.id = :order_id AND p.id_usuario = :user_id
            """),
            {"order_id": order_id, "user_id": user_id}
        ).first()

        if not order_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

        # Obtener items del pedido con detalles de productos y variantes
        items_result = db.execute(
            text("""
                SELECT pi.id, pi.cantidad, pi.precio_unitario,
                       p.id as producto_id, p.nombre, p.imagen_url
                FROM ecomerce_pedido_items pi
                JOIN ecomerce_productos p ON pi.id_producto = p.id
                WHERE pi.id_pedido = :order_id
                ORDER BY pi.id
            """),
            {"order_id": order_id}
        ).fetchall()

        items = []
        for row in items_result:
            # Calcular el total del item
            cantidad = row[1] or 0
            precio_unitario = float(row[2]) if row[2] else 0.0
            total_item = cantidad * precio_unitario

            items.append({
                "id": row[0],
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "total": total_item,
                "producto": {
                    "id": row[3],
                    "nombre": row[4],
                    "imagen_url": row[5] or "/static/img/logo.png"
                },
                "variant_data": None  # No disponible en esta tabla
            })

        return {
            "id": order_result[0],
            "fecha": str(order_result[1]) if order_result[1] else None,
            "total": float(order_result[2]) if order_result[2] else 0.0,
            "estado": order_result[3],
            "metodo_pago": order_result[4],
            "items": items
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error obteniendo detalles del pedido: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error obteniendo detalles del pedido: {str(e)}")
