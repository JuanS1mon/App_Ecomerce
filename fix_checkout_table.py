import sys
sys.path.append('.')
from db.database import get_db
from sqlalchemy import text

try:
    db = next(get_db())

    # Verificar si existe la tabla ecomerce_pedido_items
    result = db.execute(text("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = 'ecomerce_pedido_items'
    """))

    table_exists = result.fetchone()
    if table_exists:
        print('✅ Tabla ecomerce_pedido_items ya existe')
    else:
        print('❌ Tabla ecomerce_pedido_items NO existe - Creando...')

        # Crear la tabla ecomerce_pedido_items
        db.execute(text("""
            CREATE TABLE ecomerce_pedido_items (
                id INT IDENTITY(1,1) PRIMARY KEY,
                id_pedido INT NOT NULL,
                id_producto INT NOT NULL,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                nombre_producto NVARCHAR(255),
                FOREIGN KEY (id_pedido) REFERENCES ecomerce_pedidos(id),
                FOREIGN KEY (id_producto) REFERENCES ecomerce_productos(id)
            )
        """))
        db.commit()
        print('✅ Tabla ecomerce_pedido_items creada exitosamente')

    # Verificar que se creó correctamente
    result = db.execute(text("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = 'ecomerce_pedido_items'
    """))

    if result.fetchone():
        print('✅ Verificación: Tabla ecomerce_pedido_items existe')
    else:
        print('❌ Error: La tabla no se creó correctamente')

    db.close()

except Exception as e:
    print(f'❌ Error: {e}')