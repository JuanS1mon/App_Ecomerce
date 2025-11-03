import sys
sys.path.append('.')
from db.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    # Ver la estructura de la tabla
    result = db.execute(text("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ecomerce_productos' AND COLUMN_NAME = 'precio'"))
    col_info = result.fetchone()
    print(f'Columna precio: {col_info}')

    # Ver algunos valores crudos
    result = db.execute(text('SELECT TOP 3 id, nombre, precio FROM ecomerce_productos'))
    rows = result.fetchall()
    print('\nValores crudos:')
    for row in rows:
        print(f'ID {row[0]}: {row[1]} - precio: {repr(row[2])} (tipo: {type(row[2])})')

    # Ver si hay productos con precio NULL
    result = db.execute(text('SELECT COUNT(*) FROM ecomerce_productos WHERE precio IS NULL'))
    null_count = result.fetchone()[0]
    print(f'\nProductos con precio NULL: {null_count}')

    # Asignar precios a productos sin precio
    if null_count > 0:
        import random
        # Obtener IDs de productos sin precio
        result = db.execute(text('SELECT id FROM ecomerce_productos WHERE precio IS NULL'))
        null_ids = [row[0] for row in result.fetchall()]

        for prod_id in null_ids:
            new_price = round(random.uniform(10.0, 500.0), 2)
            db.execute(text('UPDATE ecomerce_productos SET precio = :price WHERE id = :id'),
                      {'price': new_price, 'id': prod_id})
            print(f'Actualizado producto {prod_id} con precio ${new_price}')

        db.commit()
        print(f'Asignados precios a {len(null_ids)} productos')

    # Verificar estadísticas finales
    result = db.execute(text('SELECT COUNT(*) as total, MIN(precio) as min_price, MAX(precio) as max_price, AVG(precio) as avg_price FROM ecomerce_productos WHERE precio IS NOT NULL'))
    stats = result.fetchone()
    print(f'\nEstadísticas finales:')
    print(f'  Total productos con precio: {stats[0]}')
    if stats[1] is not None:
        print(f'  Precio mínimo: ${stats[1]}')
        print(f'  Precio máximo: ${stats[2]}')
        print(f'  Precio promedio: ${stats[3]:.2f}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()