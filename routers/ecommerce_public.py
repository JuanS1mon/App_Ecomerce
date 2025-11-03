"""
Router para productos públicos de ecommerce
Maneja la visualización de productos y categorías para usuarios no autenticados
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel

from db.database import get_db

# Pydantic models
class ProductoPublico(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    id_categoria: int
    precio: Optional[int]
    imagen_url: Optional[str]
    active: bool

class CategoriaPublica(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    imagen_url: Optional[str]
    active: bool

router = APIRouter(
    prefix="/ecomerce/api",
    tags=["ecommerce-public"],
)

@router.get("/productos/publicos", response_model=List[ProductoPublico])
def get_productos_publicos(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    categoria: Optional[int] = Query(None, description="ID de categoría"),
    limit: int = Query(1000, description="Límite de resultados", ge=1, le=1000),
    offset: int = Query(0, description="Offset para paginación", ge=0)
):
    """
    Obtiene productos públicos con filtros opcionales
    """
    try:
        # Base query
        query = """
            SELECT id, codigo, nombre, descripcion, id_categoria, precio, imagen_url, active
            FROM ecomerce_productos
            WHERE active = 1
        """
        params = {}

        # Filtros
        conditions = []
        if search:
            conditions.append("(nombre LIKE :search OR descripcion LIKE :search OR codigo LIKE :search)")
            params['search'] = f'%{search}%'

        if categoria:
            conditions.append("id_categoria = :categoria")
            params['categoria'] = categoria

        if conditions:
            query += " AND " + " AND ".join(conditions)

        # Orden
        query += " ORDER BY nombre"

        result = db.execute(text(query), params)
        productos = result.fetchall()

        # Convertir a lista de diccionarios
        productos_list = []
        for row in productos:
            productos_list.append({
                'id': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'descripcion': row[3],
                'id_categoria': row[4],
                'precio': row[5],
                'imagen_url': row[6],
                'active': row[7]
            })

        return productos_list

    except Exception as e:
        print(f"Error obteniendo productos públicos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.get("/categorias/publicas", response_model=List[CategoriaPublica])
def get_categorias_publicas(db: Session = Depends(get_db)):
    """
    Obtiene todas las categorías activas para mostrar en la tienda
    """
    try:
        result = db.execute(text("""
            SELECT id, nombre, descripcion, imagen_url, active
            FROM ecomerce_categorias
            WHERE active = 1
            ORDER BY nombre
        """))

        categorias = []
        for row in result:
            categorias.append({
                "id": row.id,
                "nombre": row.nombre,
                "descripcion": row.descripcion,
                "imagen_url": row.imagen_url,
                "active": row.active
            })

        return categorias

    except Exception as e:
        print(f"Error obteniendo categorías públicas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/productos/{producto_id}", response_model=ProductoPublico)
def get_producto_publico(producto_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto específico por ID
    """
    try:
        result = db.execute(text("""
            SELECT id, codigo, nombre, descripcion, id_categoria, precio, imagen_url, active
            FROM ecomerce_productos
            WHERE id = :id AND active = 1
        """), {'id': producto_id})

        producto = result.fetchone()

        if not producto:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        return {
            'id': producto[0],
            'codigo': producto[1],
            'nombre': producto[2],
            'descripcion': producto[3],
            'id_categoria': producto[4],
            'precio': producto[5],
            'imagen_url': producto[6],
            'active': producto[7]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error obteniendo producto {producto_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )