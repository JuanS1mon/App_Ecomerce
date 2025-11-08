import sys
sys.path.append('.')
from db.database import get_db
from sqlalchemy import text
from datetime import datetime

db = next(get_db())

try:
    # Crear productos de prueba si no existen
    print("Creando productos de prueba...")

    # Verificar si ya existen productos
    result = db.execute(text('SELECT COUNT(*) FROM ecomerce_productos'))
    count = result.fetchone()[0]

    if count == 0:
        # Insertar productos de prueba
        products = [
            ('Producto 1', 'Descripción del producto 1', 1, 100.50, 'imagen1.jpg', 1),
            ('Producto 2', 'Descripción del producto 2', 1, 200.75, 'imagen2.jpg', 1),
            ('Producto 3', 'Descripción del producto 3', 1, 50.25, 'imagen3.jpg', 1)
        ]

        for product in products:
            db.execute(text("""
                INSERT INTO ecomerce_productos (codigo, nombre, descripcion, id_categoria, precio, imagen_url, active)
                VALUES (:codigo, :nombre, :descripcion, :id_categoria, :precio, :imagen_url, :active)
            """), {
                'codigo': f'PROD{products.index(product)+1}',
                'nombre': product[0],
                'descripcion': product[1],
                'id_categoria': product[2],
                'precio': product[3],
                'imagen_url': product[4],
                'active': product[5]
            })

        print("✅ Productos de prueba creados")

    # Crear carrito activo para el usuario 2 (test@example.com)
    print("Creando carrito activo...")

    # Verificar si ya tiene carrito activo
    result = db.execute(text('SELECT id FROM ecomerce_carritos WHERE id_usuario = 2 AND estado = \'activo\''))
    cart = result.fetchone()

    if not cart:
        # Crear carrito
        db.execute(text("""
            INSERT INTO ecomerce_carritos (id_usuario, estado, created_at)
            VALUES (2, 'activo', :created_at)
        """), {'created_at': datetime.now()})

        # Obtener ID del carrito creado
        result = db.execute(text('SELECT SCOPE_IDENTITY()'))
        cart_id = result.fetchone()[0]
        print(f"✅ Carrito creado con ID: {cart_id}")
    else:
        cart_id = cart[0]
        print(f"✅ Carrito ya existe con ID: {cart_id}")

    # Agregar productos al carrito
    print("Agregando productos al carrito...")

    # Obtener IDs de productos
    result = db.execute(text('SELECT TOP 3 id FROM ecomerce_productos ORDER BY id'))
    product_ids = [row[0] for row in result.fetchall()]

    cart_items = [
        (cart_id, product_ids[0], 2, 100.50),  # 2 unidades del producto 1
        (cart_id, product_ids[1], 1, 200.75),  # 1 unidad del producto 2
    ]

    for item in cart_items:
        db.execute(text("""
            INSERT INTO ecomerce_carrito_items (id_carrito, id_producto, cantidad, precio_unitario)
            VALUES (:id_carrito, :id_producto, :cantidad, :precio_unitario)
        """), {
            'id_carrito': item[0],
            'id_producto': item[1],
            'cantidad': item[2],
            'precio_unitario': item[3]
        })

    db.commit()
    print("✅ Productos agregados al carrito")
    print(f"Total esperado: {(2 * 100.50) + (1 * 200.75)} = {2 * 100.50 + 1 * 200.75}")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()