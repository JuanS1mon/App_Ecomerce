"""
Ejemplo de uso de la clase Cart - Programación Orientada a Objetos
"""

from sqlalchemy.orm import Session
from Services.cart_service import Cart

def ejemplo_uso_cart(db: Session, user_id: int):
    """
    Ejemplo de cómo usar la clase Cart para manejar operaciones del carrito
    """

    # Crear instancia del carrito
    cart = Cart(db, user_id)

    # Verificar si el carrito está vacío
    if cart.is_empty():
        print("El carrito está vacío")

    # Agregar productos al carrito
    try:
        # Agregar producto con ID 1, cantidad 2, precio 10.50
        item1 = cart.add_item(product_id=1, quantity=2, price=10.50)
        print(f"Producto agregado: {item1}")

        # Agregar otro producto
        item2 = cart.add_item(product_id=2, quantity=1, price=25.00)
        print(f"Producto agregado: {item2}")

        # Actualizar cantidad del primer item
        updated_item = cart.update_item_quantity(item1['id'], 5)
        print(f"Item actualizado: {updated_item}")

        # Obtener información del carrito
        print(f"Total del carrito: ${cart.get_total()}")
        print(f"Número de items: {cart.get_item_count()}")
        print(f"Carrito vacío: {cart.is_empty()}")

        # Obtener todos los items
        for item in cart.items:
            print(f"Item: {item}")

        # Remover un item
        removed_item = cart.remove_item(item2['id'])
        print(f"Item removido: {removed_item}")

        # Convertir carrito a diccionario
        cart_dict = cart.to_dict()
        print(f"Información del carrito: {cart_dict}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()

    # Limpiar el carrito (opcional)
    # cart.clear()

if __name__ == "__main__":
    # Este es solo un ejemplo - en la práctica usarías una sesión de DB real
    print("Ejemplo de uso de la clase Cart")
    print("Para usar en producción:")
    print("1. Importar: from Services.cart_service import Cart")
    print("2. Crear instancia: cart = Cart(db_session, user_id)")
    print("3. Usar métodos: cart.add_item(), cart.get_total(), etc.")