# ============================================================================
# ROUTER OPTIMIZADO: CONFIGURACION
# ============================================================================
"""
Router FastAPI optimizado para configuracion
Parte del servicio: tienda_online
Usa async/await inteligentemente basado en la complejidad de las operaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from db.database import get_db, get_async_db
from .service_configuracion import configuracion_service
from .schema_configuracion import Configuracion, ConfiguracionCreate, ConfiguracionUpdate

router = APIRouter(
    prefix="/configuracion",
    tags=["configuracion"],
    responses={404: {"description": "No encontrado"}}
)

# ============================================================================
# CREATE - ASYNC
# ============================================================================

@router.post("/", response_model=Configuracion, status_code=status.HTTP_201_CREATED)
async def create_configuracion(
    obj_in: ConfiguracionCreate,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Crear nuevo configuracion
    ✅ ASYNC - Operación de escritura optimizada para concurrencia
    """
    return await configuracion_service.create_async(db=db, obj_in=obj_in)

# ============================================================================
# LIST - ASYNC
# ============================================================================

@router.get("/", response_model=List[Configuracion])
async def read_configuracion_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener lista de configuracion
    ✅ ASYNC - Lista optimizada para grandes volúmenes de datos
    """
    if search:
        return await configuracion_service.search_async(db=db, query=search, skip=skip, limit=limit)
    return await configuracion_service.get_multi_async(db=db, skip=skip, limit=limit)

# ============================================================================
# GET BY ID - SYNC
# ============================================================================

@router.get("/{id}", response_model=Configuracion)
def read_configuracion(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener configuracion por id
    ⚡ SYNC - Operación simple y rápida
    """
    db_obj = configuracion_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuracion no encontrado"
        )
    return db_obj

# ============================================================================
# UPDATE - ASYNC
# ============================================================================

@router.put("/{id}", response_model=Configuracion)
async def update_configuracion(
    id: int,
    obj_in: ConfiguracionUpdate,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Actualizar configuracion
    ✅ ASYNC - Actualización optimizada con posibles efectos en cascada
    """
    db_obj = await configuracion_service.get_async(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuracion no encontrado"
        )
    return await configuracion_service.update_async(db=db, db_obj=db_obj, obj_in=obj_in)

# ============================================================================
# DELETE - ASYNC
# ============================================================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_configuracion(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Eliminar configuracion
    ✅ ASYNC - Eliminación con posibles cascadas y limpieza en background
    """
    success = await configuracion_service.delete_async(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuracion no encontrado"
        )
    
    # Ejecutar limpieza en background si es necesario
    if background_tasks:
        background_tasks.add_task(configuracion_service.cleanup_after_delete, id)


# ============================================================================
# HEALTH CHECK - SIEMPRE SYNC
# ============================================================================

@router.get("/health")
def health_check():
    """
    Health check del servicio
    ⚡ SYNC - Verificación simple y rápida
    """
    return {"status": "healthy", "service": "configuracion"}
