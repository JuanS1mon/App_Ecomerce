# ============================================================================
# ROUTER OPTIMIZADO: PRODUCTOS
# ============================================================================
"""
Router FastAPI optimizado para productos
Parte del servicio: tienda_online
Usa async/await inteligentemente basado en la complejidad de las operaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from db.database import get_db, get_async_db
from .service_productos import productos_service
from .schema_productos import Productos, ProductosCreate, ProductosUpdate

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
    responses={404: {"description": "No encontrado"}}
)

# ============================================================================
# CREATE - ASYNC
# ============================================================================

@router.post("/", response_model=Productos, status_code=status.HTTP_201_CREATED)
async def create_productos(
    obj_in: ProductosCreate,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Crear nuevo productos
    ✅ ASYNC - Operación de escritura optimizada para concurrencia
    """
    return await productos_service.create_async(db=db, obj_in=obj_in)

# ============================================================================
# LIST - ASYNC
# ============================================================================

@router.get("/", response_model=List[Productos])
async def read_productos_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener lista de productos
    ✅ ASYNC - Lista optimizada para grandes volúmenes de datos
    """
    if search:
        return await productos_service.search_async(db=db, query=search, skip=skip, limit=limit)
    return await productos_service.get_multi_async(db=db, skip=skip, limit=limit)

# ============================================================================
# GET BY ID - ASYNC
# ============================================================================

@router.get("/{id}", response_model=Productos)
async def read_productos(
    id: int,
    include_relations: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener productos por id
    ✅ ASYNC - Tabla compleja que puede beneficiarse de carga optimizada
    """
    db_obj = await productos_service.get_async(
        db=db, id=id, include_relations=include_relations
    )
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos no encontrado"
        )
    return db_obj

# ============================================================================
# UPDATE - ASYNC
# ============================================================================

@router.put("/{id}", response_model=Productos)
async def update_productos(
    id: int,
    obj_in: ProductosUpdate,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Actualizar productos
    ✅ ASYNC - Actualización optimizada con posibles efectos en cascada
    """
    db_obj = await productos_service.get_async(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos no encontrado"
        )
    return await productos_service.update_async(db=db, db_obj=db_obj, obj_in=obj_in)

# ============================================================================
# DELETE - ASYNC
# ============================================================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_productos(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Eliminar productos
    ✅ ASYNC - Eliminación con posibles cascadas y limpieza en background
    """
    success = await productos_service.delete_async(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos no encontrado"
        )
    
    # Ejecutar limpieza en background si es necesario
    if background_tasks:
        background_tasks.add_task(productos_service.cleanup_after_delete, id)


# ============================================================================
# ENDPOINTS ADICIONALES PARA TABLA COMPLEJA
# ============================================================================

@router.get("/count", response_model=int)
async def count_productos(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Contar registros de productos"""
    return await productos_service.count_async(db=db, search=search)

@router.post("/bulk", response_model=List[Productos])
async def bulk_create_productos(
    objects: List[ProductosCreate],
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """Crear múltiples productos en lote"""
    return await productos_service.bulk_create_async(db=db, objects=objects)


# ============================================================================
# HEALTH CHECK - SIEMPRE SYNC
# ============================================================================

@router.get("/health")
def health_check():
    """
    Health check del servicio
    ⚡ SYNC - Verificación simple y rápida
    """
    return {"status": "healthy", "service": "productos"}
