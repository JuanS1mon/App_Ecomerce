import sys
sys.path.append('.')
from db.database import get_db
from sqlalchemy import text
import random

db = next(get_db())
try:
    # Ver categorías disponibles
    result = db.execute(text('SELECT id, nombre FROM ecomerce_categorias'))
    categories = result.fetchall()
    print('Categorías disponibles:')
    for cat in categories:
        print(f'  {cat[0]}: {cat[1]}')

    # Productos de ejemplo para generar más datos
    product_templates = [
        # Electrónicos
        ("Laptop Dell XPS 13", "Laptop ultrabook premium con pantalla 4K", 1, 1200, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"),
        ("iPhone 15 Pro", "Smartphone Apple con chip A17 Pro", 1, 999, "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"),
        ("Samsung Galaxy S24", "Smartphone Android con cámara de 200MP", 1, 899, "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400"),
        ("MacBook Air M3", "Laptop Apple con chip M3", 1, 1099, "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400"),
        ("iPad Pro 12.9", "Tablet profesional con Apple Pencil", 1, 799, "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400"),

        # Audio
        ("Sony WH-1000XM5", "Audífonos inalámbricos con cancelación de ruido", 2, 299, "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400"),
        ("Bose QuietComfort", "Audífonos premium con cancelación activa", 2, 279, "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400"),
        ("AirPods Pro", "Audífonos inalámbricos con cancelación de ruido", 2, 249, "https://images.unsplash.com/photo-1606220945770-b5b6c2c9bf1d?w=400"),
        ("JBL Go 3", "Altavoz portátil resistente al agua", 2, 39, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"),

        # Gaming
        ("Nintendo Switch OLED", "Consola híbrida con pantalla OLED", 3, 349, "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400"),
        ("PlayStation 5", "Consola de nueva generación", 3, 499, "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400"),
        ("Xbox Series X", "Consola Microsoft de alta potencia", 3, 499, "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=400"),
        ("Steam Deck", "PC gaming portátil de Valve", 3, 399, "https://images.unsplash.com/photo-1625842268584-8f3296236761?w=400"),

        # Ropa
        ("Nike Air Max", "Zapatillas deportivas icónicas", 4, 129, "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400"),
        ("Adidas Ultraboost", "Zapatillas running con amortiguación", 4, 189, "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400"),
        ("Levi's 501", "Jeans clásicos originales", 4, 89, "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400"),
        ("H&M Basic Tee", "Camiseta básica de algodón", 4, 12, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"),

        # Hogar
        ("Nespresso Vertuo", "Máquina de café con cápsulas", 5, 199, "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400"),
        ("Dyson V15", "Aspiradora inalámbrica detect", 5, 699, "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"),
        ("Instant Pot Duo", "Olla a presión multifunción", 5, 89, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"),
        ("Philips Hue Starter", "Kit de iluminación inteligente", 5, 99, "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400"),
    ]

    # Generar productos adicionales
    print(f'\nGenerando productos adicionales...')
    inserted_count = 0

    for i in range(50):  # Generar 50 productos adicionales
        template = random.choice(product_templates)
        nombre, descripcion, categoria_id, precio_base, imagen_base = template

        # Variaciones aleatorias
        precio = precio_base + random.randint(-20, 50)
        codigo = f'PROD{100+i:03d}'

        # Variar nombre ligeramente
        variaciones = ['', ' Plus', ' Pro', ' Premium', ' Lite', ' Max']
        nombre_final = nombre + random.choice(variaciones)

        # Insertar producto
        db.execute(text("""
            INSERT INTO ecomerce_productos (codigo, nombre, descripcion, id_categoria, precio, imagen_url, active)
            VALUES (:codigo, :nombre, :descripcion, :id_categoria, :precio, :imagen_url, :active)
        """), {
            'codigo': codigo,
            'nombre': nombre_final,
            'descripcion': descripcion,
            'id_categoria': categoria_id,
            'precio': precio,
            'imagen_url': imagen_base,
            'active': True
        })

        inserted_count += 1

    db.commit()
    print(f'✅ Insertados {inserted_count} productos adicionales')

    # Verificar total final
    result = db.execute(text('SELECT COUNT(*) as total FROM ecomerce_productos'))
    total_final = result.fetchone()[0]
    print(f'📊 Total de productos ahora: {total_final}')

except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()