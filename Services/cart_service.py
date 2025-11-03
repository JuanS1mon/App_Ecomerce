"""
Clase Cart - Programación Orientada a Objetos para manejar carritos de compras
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Cart:
    """
    Clase que representa un carrito de compras y maneja todas las operaciones relacionadas
    """

    def __init__(self, db: Session, user_id: int):
        """
        Inicializa una instancia de Cart

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario del carrito
        """
        self.db = db
        self.user_id = user_id
        self.cart_id: Optional[int] = None
        self.items: List[Dict[str, Any]] = []

        # Limpiar carritos duplicados antes de cargar/crear
        self.cleanup_duplicate_carts()
        self._load_or_create_cart()

    def _load_or_create_cart(self) -> None:
        """
        Carga el carrito activo del usuario o crea uno nuevo si no existe
        """
        try:
            # Buscar carrito activo del usuario
            cart_result = self.db.execute(
                text("SELECT TOP 1 id FROM ecomerce_carritos WHERE id_usuario = :user_id AND estado = 'activo' ORDER BY created_at DESC"),
                {"user_id": self.user_id}
            ).first()

            if cart_result:
                self.cart_id = cart_result[0]
                logger.info(f"Carrito activo encontrado para usuario {self.user_id}: ID {self.cart_id}")
                self._load_items()
            else:
                logger.info(f"No se encontró carrito activo para usuario {self.user_id}, creando uno nuevo")
                self._create_cart()
        except Exception as e:
            logger.error(f"Error al cargar/crear carrito para usuario {self.user_id}: {e}")
            raise

    def _create_cart(self) -> None:
        """
        Crea un nuevo carrito activo para el usuario
        """
        try:
            cart_query = text("""
                INSERT INTO ecomerce_carritos (id_usuario, estado, created_at)
                OUTPUT INSERTED.id
                VALUES (:user_id, 'activo', GETDATE())
            """)
            cart_result = self.db.execute(cart_query, {"user_id": self.user_id})
            self.cart_id = cart_result.first()[0]
            self.items = []
            logger.info(f"Carrito creado para usuario {self.user_id} con ID {self.cart_id}")
        except Exception as e:
            logger.error(f"Error al crear carrito: {e}")
            raise

    def _load_items(self) -> None:
        """
        Carga los items del carrito desde la base de datos
        """
        try:
            result = self.db.execute(
                text("SELECT id, id_carrito, id_producto, cantidad, precio_unitario FROM ecomerce_carrito_items WHERE id_carrito = :cart_id"),
                {"cart_id": self.cart_id}
            )

            self.items = []
            for row in result.fetchall():
                self.items.append({
                    'id': row[0],
                    'id_carrito': row[1],
                    'id_producto': row[2],
                    'cantidad': row[3],
                    'precio_unitario': row[4]
                })
        except Exception as e:
            logger.error(f"Error al cargar items del carrito: {e}")
            raise

    def add_item(self, product_id: int, quantity: int = 1, price: float = 0.0) -> Dict[str, Any]:
        """
        Agrega un producto al carrito

        Args:
            product_id: ID del producto
            quantity: Cantidad a agregar
            price: Precio unitario del producto

        Returns:
            Diccionario con la información del item agregado/actualizado
        """
        try:
            # Verificar si el producto ya está en el carrito
            existing_item = None
            for item in self.items:
                if item['id_producto'] == product_id:
                    existing_item = item
                    break

            if existing_item:
                # Actualizar cantidad existente
                new_quantity = existing_item['cantidad'] + quantity
                return self.update_item_quantity(existing_item['id'], new_quantity)
            else:
                # Crear nuevo item
                insert_query = text("""
                    INSERT INTO ecomerce_carrito_items (id_carrito, id_producto, cantidad, precio_unitario)
                    OUTPUT INSERTED.id, INSERTED.id_carrito, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario
                    VALUES (:cart_id, :product_id, :quantity, :price)
                """)
                result = self.db.execute(insert_query, {
                    "cart_id": self.cart_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": price
                })

                row = result.first()
                self.db.commit()

                new_item = {
                    'id': row[0],
                    'id_carrito': row[1],
                    'id_producto': row[2],
                    'cantidad': row[3],
                    'precio_unitario': row[4]
                }

                self.items.append(new_item)
                logger.info(f"Producto {product_id} agregado al carrito {self.cart_id}")
                return new_item

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al agregar producto al carrito: {e}")
            raise

    def update_item_quantity(self, item_id: int, new_quantity: int) -> Dict[str, Any]:
        """
        Actualiza la cantidad de un item del carrito

        Args:
            item_id: ID del item del carrito
            new_quantity: Nueva cantidad

        Returns:
            Diccionario con la información del item actualizado
        """
        try:
            if new_quantity <= 0:
                return self.remove_item(item_id)

            update_query = text("""
                UPDATE ecomerce_carrito_items
                SET cantidad = :quantity
                OUTPUT INSERTED.id, INSERTED.id_carrito, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario
                WHERE id = :item_id
            """)
            result = self.db.execute(update_query, {"quantity": new_quantity, "item_id": item_id})
            row = result.first()

            if not row:
                raise ValueError(f"Item {item_id} no encontrado en el carrito")

            self.db.commit()

            updated_item = {
                'id': row[0],
                'id_carrito': row[1],
                'id_producto': row[2],
                'cantidad': row[3],
                'precio_unitario': row[4]
            }

            # Actualizar en la lista local
            for i, item in enumerate(self.items):
                if item['id'] == item_id:
                    self.items[i] = updated_item
                    break

            logger.info(f"Cantidad del item {item_id} actualizada a {new_quantity}")
            return updated_item

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar cantidad del item: {e}")
            raise

    def remove_item(self, item_id: int) -> Dict[str, Any]:
        """
        Remueve un item del carrito

        Args:
            item_id: ID del item a remover

        Returns:
            Diccionario con la información del item removido
        """
        try:
            # Obtener el item antes de eliminarlo
            item_to_remove = None
            for item in self.items:
                if item['id'] == item_id:
                    item_to_remove = item
                    break

            if not item_to_remove:
                raise ValueError(f"Item {item_id} no encontrado en el carrito")

            delete_query = text("""
                DELETE FROM ecomerce_carrito_items
                OUTPUT DELETED.id, DELETED.id_carrito, DELETED.id_producto, DELETED.cantidad, DELETED.precio_unitario
                WHERE id = :item_id
            """)
            result = self.db.execute(delete_query, {"item_id": item_id})
            row = result.first()

            if not row:
                raise ValueError(f"Error al eliminar item {item_id}")

            self.db.commit()

            # Remover de la lista local
            self.items = [item for item in self.items if item['id'] != item_id]

            logger.info(f"Item {item_id} removido del carrito {self.cart_id}")
            return {
                'id': row[0],
                'id_carrito': row[1],
                'id_producto': row[2],
                'cantidad': row[3],
                'precio_unitario': row[4]
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al remover item del carrito: {e}")
            raise

    def get_total(self) -> float:
        """
        Calcula el total del carrito

        Returns:
            Total del carrito
        """
        return sum(item['cantidad'] * item['precio_unitario'] for item in self.items)

    def get_item_count(self) -> int:
        """
        Obtiene el número total de items en el carrito

        Returns:
            Número total de items
        """
        return sum(item['cantidad'] for item in self.items)

    def is_empty(self) -> bool:
        """
        Verifica si el carrito está vacío

        Returns:
            True si el carrito está vacío, False en caso contrario
        """
        return len(self.items) == 0

    def clear(self) -> None:
        """
        Vacía completamente el carrito
        """
        try:
            if self.cart_id:
                self.db.execute(
                    text("DELETE FROM ecomerce_carrito_items WHERE id_carrito = :cart_id"),
                    {"cart_id": self.cart_id}
                )
                self.db.commit()
                self.items = []
                logger.info(f"Carrito {self.cart_id} vaciado")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al vaciar carrito: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el carrito a un diccionario

        Returns:
            Diccionario con la información del carrito
        """
        return {
            'id': self.cart_id,
            'user_id': self.user_id,
            'items': self.items,
            'total': self.get_total(),
            'item_count': self.get_item_count(),
            'is_empty': self.is_empty()
        }

    def cleanup_duplicate_carts(self) -> None:
        """
        Limpia carritos duplicados para el usuario, dejando solo el más reciente activo
        """
        try:
            # Obtener todos los carritos activos del usuario ordenados por fecha descendente
            all_active_carts = self.db.execute(
                text("SELECT id FROM ecomerce_carritos WHERE id_usuario = :user_id AND estado = 'activo' ORDER BY created_at DESC"),
                {"user_id": self.user_id}
            ).fetchall()

            if len(all_active_carts) > 1:
                logger.warning(f"Usuario {self.user_id} tiene {len(all_active_carts)} carritos activos. Limpiando...")

                # Mantener solo el más reciente (el primero)
                keep_cart_id = all_active_carts[0][0]

                # Marcar los demás como inactivos
                cart_ids_to_deactivate = [cart[0] for cart in all_active_carts[1:]]

                if cart_ids_to_deactivate:
                    # Primero, mover los items de los carritos antiguos al carrito activo
                    for old_cart_id in cart_ids_to_deactivate:
                        # Obtener items del carrito antiguo
                        old_items = self.db.execute(
                            text("SELECT id_producto, cantidad, precio_unitario FROM ecomerce_carrito_items WHERE id_carrito = :cart_id"),
                            {"cart_id": old_cart_id}
                        ).fetchall()

                        # Agregar cada item al carrito activo
                        for item in old_items:
                            # Verificar si el producto ya existe en el carrito activo
                            existing_item = self.db.execute(
                                text("SELECT id, cantidad FROM ecomerce_carrito_items WHERE id_carrito = :cart_id AND id_producto = :product_id"),
                                {"cart_id": keep_cart_id, "product_id": item[0]}
                            ).first()

                            if existing_item:
                                # Actualizar cantidad
                                new_quantity = existing_item[1] + item[1]
                                self.db.execute(
                                    text("UPDATE ecomerce_carrito_items SET cantidad = :quantity WHERE id = :item_id"),
                                    {"quantity": new_quantity, "item_id": existing_item[0]}
                                )
                            else:
                                # Insertar nuevo item
                                self.db.execute(
                                    text("INSERT INTO ecomerce_carrito_items (id_carrito, id_producto, cantidad, precio_unitario) VALUES (:cart_id, :product_id, :quantity, :price)"),
                                    {"cart_id": keep_cart_id, "product_id": item[0], "quantity": item[1], "price": item[2]}
                                )

                        # Eliminar items del carrito antiguo
                        self.db.execute(
                            text("DELETE FROM ecomerce_carrito_items WHERE id_carrito = :cart_id"),
                            {"cart_id": old_cart_id}
                        )

                    # Marcar carritos antiguos como inactivos
                    for old_cart_id in cart_ids_to_deactivate:
                        self.db.execute(
                            text("UPDATE ecomerce_carritos SET estado = 'inactivo' WHERE id = :cart_id"),
                            {"cart_id": old_cart_id}
                        )

                    self.db.commit()
                    logger.info(f"Limpieza completada para usuario {self.user_id}. Carrito activo: {keep_cart_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al limpiar carritos duplicados para usuario {self.user_id}: {e}")
            raise