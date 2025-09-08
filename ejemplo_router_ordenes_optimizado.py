# ============================================================================
# ROUTER OPTIMIZADO: ORDENES
# ============================================================================
"""
Router FastAPI optimizado para ordenes
Parte del servicio: tienda_online
Usa async/await inteligentemente basado en la complejidad de las operaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from sql_app.db.database import get_db, get_async_db
from .service_ordenes import ordenes_service
from .schema_ordenes import Ordenes, OrdenesCreate, OrdenesUpdate

router = APIRouter(
    prefix="/ordenes",
    tags=["ordenes"],
    responses={404: {"description": "No encontrado"}}
)

# ============================================================================
# CREATE - ASYNC
# ============================================================================

@router.post("/", response_model=Ordenes, status_code=status.HTTP_201_CREATED)
async def create_ordenes(
    obj_in: OrdenesCreate,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Crear nuevo ordenes
    ✅ ASYNC - Operación de escritura optimizada para concurrencia
    """
    return await ordenes_service.create_async(db=db, obj_in=obj_in)

# ============================================================================
# LIST - ASYNC
# ============================================================================

@router.get("/", response_model=List[Ordenes])
async def read_ordenes_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener lista de ordenes
    ✅ ASYNC - Lista optimizada para grandes volúmenes de datos
    """
    if search:
        return await ordenes_service.search_async(db=db, query=search, skip=skip, limit=limit)
    return await ordenes_service.get_multi_async(db=db, skip=skip, limit=limit)

# ============================================================================
# GET BY ID - ASYNC
# ============================================================================

@router.get("/{id}", response_model=Ordenes)
async def read_ordenes(
    id: int,
    include_relations: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener ordenes por id
    ✅ ASYNC - Tabla compleja que puede beneficiarse de carga optimizada
    """
    db_obj = await ordenes_service.get_async(
        db=db, id=id, include_relations=include_relations
    )
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordenes no encontrado"
        )
    return db_obj

# ============================================================================
# UPDATE - ASYNC
# ============================================================================

@router.put("/{id}", response_model=Ordenes)
async def update_ordenes(
    id: int,
    obj_in: OrdenesUpdate,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Actualizar ordenes
    ✅ ASYNC - Actualización optimizada con posibles efectos en cascada
    """
    db_obj = await ordenes_service.get_async(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordenes no encontrado"
        )
    return await ordenes_service.update_async(db=db, db_obj=db_obj, obj_in=obj_in)

# ============================================================================
# DELETE - ASYNC
# ============================================================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ordenes(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Eliminar ordenes
    ✅ ASYNC - Eliminación con posibles cascadas y limpieza en background
    """
    success = await ordenes_service.delete_async(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordenes no encontrado"
        )
    
    # Ejecutar limpieza en background si es necesario
    if background_tasks:
        background_tasks.add_task(ordenes_service.cleanup_after_delete, id)


# ============================================================================
# ENDPOINTS ADICIONALES PARA TABLA COMPLEJA
# ============================================================================

@router.get("/count", response_model=int)
async def count_ordenes(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Contar registros de ordenes"""
    return await ordenes_service.count_async(db=db, search=search)

@router.post("/bulk", response_model=List[Ordenes])
async def bulk_create_ordenes(
    objects: List[OrdenesCreate],
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """Crear múltiples ordenes en lote"""
    return await ordenes_service.bulk_create_async(db=db, objects=objects)


# ============================================================================
# HEALTH CHECK - SIEMPRE SYNC
# ============================================================================

@router.get("/health")
def health_check():
    """
    Health check del servicio
    ⚡ SYNC - Verificación simple y rápida
    """
    return {"status": "healthy", "service": "ordenes"}
