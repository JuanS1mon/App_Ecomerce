from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy import text
from db.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/productos/tienda", response_class=HTMLResponse)
async def get_tienda_productos():
    """
    Muestra la página de tienda de productos
    """
    try:
        # Ruta al template
        script_dir = Path(__file__).parent
        html_path = script_dir / "Projects" / "ecomerce" / "templates" / "productos_tienda.html"

        if not html_path.exists():
            raise HTTPException(status_code=404, detail="Template de tienda no encontrado")

        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de tienda de productos: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener la pagina HTML de tienda de productos.")

@router.get("/productos/detalle/{id}", response_class=HTMLResponse)
async def get_detalle_producto(id: int):
    """
    Muestra la página de detalle de un producto
    """
    try:
        # Ruta al template
        script_dir = Path(__file__).parent
        html_path = script_dir / "Projects" / "ecomerce" / "templates" / f"producto_detalle.html"

        if not html_path.exists():
            raise HTTPException(status_code=404, detail="Template no encontrado")

        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML de detalle de producto: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener la pagina HTML de detalle de producto.")

@router.get("/productos/publico/{id}")
def get_producto_publico(id: int):
    """
    Obtiene un producto público específico por ID
    """
    try:
        db = next(get_db())
        # Usar JOIN para obtener producto con sus variantes en una sola consulta
        result = db.execute(text("""
            SELECT
                p.id, p.codigo, p.nombre, p.descripcion, p.id_categoria, p.precio, p.imagen_url, p.active,
                v.id as variant_id, v.tipo as variant_nombre, v.precio_adicional, v.stock, v.active as variant_active
            FROM ecomerce_productos p
            LEFT JOIN ecomerce_product_variants v ON p.id = v.product_id AND v.active = 1
            WHERE p.active = 1 AND p.id = :id
            ORDER BY v.tipo
        """), {"id": id})

        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # El primer row contiene la información del producto
        row = rows[0]
        producto = {
            'id': row[0],
            'codigo': row[1],
            'nombre': row[2],
            'descripcion': row[3],
            'id_categoria': row[4],
            'precio': row[5],
            'imagen_url': row[6],
            'active': row[7],
            'variants': []
        }

        # Agregar todas las variantes
        for row in rows:
            if row[8] is not None:  # variant_id no es null
                producto['variants'].append({
                    "id": row[8],
                    "nombre": row[9],
                    "precio_adicional": row[10],
                    "stock": row[11],
                    "active": row[12]
                })

        return producto

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto público {id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

# API Routes
@router.get("/api/productos/publicos")
def get_productos_publicos():
    """
    Obtiene productos públicos para la tienda
    """
    try:
        db = next(get_db())
        # Usar JOIN para obtener productos con sus variantes en una sola consulta
        result = db.execute(text("""
            SELECT
                p.id, p.codigo, p.nombre, p.descripcion, p.id_categoria, p.precio, p.imagen_url, p.active,
                v.id as variant_id, v.tipo as variant_nombre, v.precio_adicional, v.stock, v.active as variant_active
            FROM ecomerce_productos p
            LEFT JOIN ecomerce_product_variants v ON p.id = v.product_id AND v.active = 1
            WHERE p.active = 1
            ORDER BY p.nombre, v.tipo
        """))

        productos_dict = {}
        for row in result:
            product_id = row[0]
            if product_id not in productos_dict:
                productos_dict[product_id] = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'descripcion': row[3],
                    'id_categoria': row[4],
                    'precio': row[5],
                    'imagen_url': row[6],
                    'active': row[7],
                    'variants': []
                }

            # Agregar variante si existe
            if row[8] is not None:  # variant_id no es null
                productos_dict[product_id]['variants'].append({
                    "id": row[8],
                    "nombre": row[9],
                    "precio_adicional": row[10],
                    "stock": row[11],
                    "active": row[12]
                })

        productos = list(productos_dict.values())
        return productos

    except Exception as e:
        logger.error(f"Error obteniendo productos públicos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.get("/api/categorias/publicas")
def get_categorias_publicas():
    """
    Obtiene todas las categorías activas para mostrar en la tienda
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
        logger.error(f"Error obteniendo categorías públicas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")