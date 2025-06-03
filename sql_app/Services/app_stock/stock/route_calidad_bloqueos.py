from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
try:
    from ...db.database import get_db
except ImportError:
    from sql_app.db.database import get_db
# Configurar logger
logger = logging.getLogger(__name__)

# Configurar templates
templates = Jinja2Templates(directory="static")

# Crear router para bloqueos de calidad
router = APIRouter(
    prefix="/stock/calidad",
    tags=["stock_calidad"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/bloquear", response_model=Dict[str, Any])
async def api_bloquear_stock(
    id_deposito: int,
    codigo_art: int,
    cantidad: float,
    motivo: str,
    usuario: Optional[str] = None,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Bloquea una cantidad de stock por motivos de calidad.
    """
    try:
        resultado = bloquear_stock_por_calidad(
            db, 
            id_deposito, 
            codigo_art, 
            cantidad, 
            motivo,
            usuario,
            observaciones
        )
        return resultado
    except Exception as e:
        logger.error(f"Error al bloquear stock: {e}")
        raise

@router.post("/liberar/{id_bloqueo}", response_model=Dict[str, Any])
async def api_liberar_stock(
    id_bloqueo: int,
    usuario: Optional[str] = None,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Libera un bloqueo de stock por calidad.
    """
    try:
        resultado = liberar_stock_bloqueado(
            db, 
            id_bloqueo,
            usuario,
            observaciones
        )
        return resultado
    except Exception as e:
        logger.error(f"Error al liberar bloqueo: {e}")
        raise

@router.get("/lista", response_model=List[Dict[str, Any]])
async def api_listar_bloqueos(
    id_deposito: Optional[int] = None,
    codigo_art: Optional[int] = None,
    solo_activos: bool = Query(True, description="Si es True, solo muestra bloqueos activos"),
    db: Session = Depends(get_db)
):
    """
    Lista los bloqueos de stock por calidad, con opción de filtrar por depósito y/o artículo.
    """
    try:
        bloqueos = listar_bloqueos_calidad(
            db, 
            id_deposito, 
            codigo_art,
            solo_activos
        )
        return bloqueos
    except Exception as e:
        logger.error(f"Error al listar bloqueos: {e}")
        raise

@router.get("/", response_class=HTMLResponse)
async def get_calidad_bloqueos_page(request: Request):
    """
    Devuelve la página HTML para el módulo de control de calidad y bloqueos.
    """
    try:
        return templates.TemplateResponse("app_stock/stock/calidad_bloqueos.html", {"request": request})
    except Exception as e:
        logger.error(f"Error al obtener la página de control de calidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar la página: {str(e)}"
        )
