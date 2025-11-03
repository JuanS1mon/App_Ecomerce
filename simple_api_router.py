from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from db.database import get_db

router = APIRouter(prefix="/ecomerce/api", tags=["ecommerce-api"])

@router.get("/productos/publicos")
def get_productos_publicos():
    """
    Obtiene productos públicos
    """
    try:
        db = next(get_db())
        result = db.execute(text("""
            SELECT id, codigo, nombre, descripcion, id_categoria, precio, imagen_url, active
            FROM ecomerce_productos
            WHERE active = 1
            ORDER BY nombre
        """))

        productos = []
        for row in result:
            productos.append({
                'id': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'descripcion': row[3],
                'id_categoria': row[4],
                'precio': row[5],
                'imagen_url': row[6],
                'active': row[7],
                'variants': []
            })

        return productos

    except Exception as e:
        print(f"Error obteniendo productos públicos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.get("/categorias/publicas")
def get_categorias_publicas():
    """
    Obtiene todas las categorías activas
    """
    try:
        db = next(get_db())
        result = db.execute(text("""
            SELECT id, nombre, descripcion, imagen_url, active
            FROM ecomerce_categorias
            WHERE active = 1
            ORDER BY nombre
        """))

        categorias = []
        for row in result:
            categorias.append({
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "imagen_url": row[3],
                "active": row[4]
            })

        return categorias

    except Exception as e:
        print(f"Error obteniendo categorías públicas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")