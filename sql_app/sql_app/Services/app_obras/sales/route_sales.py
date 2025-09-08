# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session

# Imports del proyecto
from ....db.database import get_db
from .model_sales import Sales as SalesModel
from .schema_sales import SalesCreate, SalesUpdate, SalesRead
from .service_sales import (
    create_sales, get_sales, get_all_sales, delete_sales, update_sales,
    get_sales_by_artwork, get_sales_by_year, get_sales_by_gallery, 
    get_sales_by_payment_status, get_pending_payments, calculate_artist_earnings,
    get_sales_summary_by_year
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=SalesRead, status_code=status.HTTP_201_CREATED)
async def routes_post_sales(sales: SalesCreate, db: Session = Depends(get_db)):
    required_fields = [sales.artwork_id, sales.sale_year, sales.gallery, sales.buyer_collection]
    if not all(required_fields):
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos artwork_id, sale_year, gallery y buyer_collection son obligatorios")
    try:
        sales_model = SalesModel(**sales.model_dump())
        db_sales = create_sales(db=db, sales=sales_model)
        return SalesRead.model_validate(db_sales)
    except Exception as e:
        logger.error(f"Error al crear Sales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=SalesRead)
async def routes_get_sales_id(id: int, db: Session = Depends(get_db)):
    try:
        db_sales = get_sales(db, id)
        if not db_sales:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales no encontrado")
        return SalesRead.model_validate(db_sales)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Sales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[SalesRead])
async def routes_get_all_sales(
    skip: int = 0, 
    limit: int = 100, 
    artwork_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    gallery: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    pending_only: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    try:
        if pending_only:
            db_sales = get_pending_payments(db)
        elif artwork_id:
            db_sales = get_sales_by_artwork(db, artwork_id)
        elif year:
            db_sales = get_sales_by_year(db, year)
        elif gallery:
            db_sales = get_sales_by_gallery(db, gallery)
        elif payment_status:
            db_sales = get_sales_by_payment_status(db, payment_status)
        else:
            db_sales = get_all_sales(db, skip=skip, limit=limit)
        
        return [SalesRead.model_validate(sale) for sale in db_sales]
    except Exception as e:
        logger.error(f"Error al obtener lista de Sales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_sales(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_sales(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Sales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.put("/id/{id}", response_model=SalesRead)
async def routes_update_sales(id: int, sales: SalesUpdate, db: Session = Depends(get_db)):
    try:
        db_sales = update_sales(db, id, sales)
        if not db_sales:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales no encontrado")
        return SalesRead.model_validate(db_sales)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Sales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

# Endpoints especiales para reportes
@router.get("/artist-earnings/{artwork_id}")
async def routes_get_artist_earnings(artwork_id: int, db: Session = Depends(get_db)):
    """Calcular ganancias del artista para una obra específica"""
    try:
        earnings = calculate_artist_earnings(db, artwork_id)
        return {"artwork_id": artwork_id, "total_artist_earnings": float(earnings)}
    except Exception as e:
        logger.error(f"Error al calcular ganancias del artista: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al calcular ganancias.")

@router.get("/summary/{year}")
async def routes_get_sales_summary(year: int, db: Session = Depends(get_db)):
    """Obtener resumen de ventas por año"""
    try:
        summary = get_sales_summary_by_year(db, year)
        return summary
    except Exception as e:
        logger.error(f"Error al obtener resumen de ventas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener resumen.")

@router.get("/pending/", response_model=List[SalesRead])
async def routes_get_pending_payments(db: Session = Depends(get_db)):
    """Obtener todas las ventas con pagos pendientes"""
    try:
        db_sales = get_pending_payments(db)
        return [SalesRead.model_validate(sale) for sale in db_sales]
    except Exception as e:
        logger.error(f"Error al obtener pagos pendientes: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener pagos pendientes.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_sales_html(request: Request, db: Session = Depends(get_db)):
    try:
        sales = get_all_sales(db)
        return templates.TemplateResponse("app_obras/sales/list.html", {
            "request": request,
            "sales": sales
        })
    except Exception as e:
        logger.error(f"Error al cargar página de sales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_sales_html(request: Request):
    return templates.TemplateResponse("app_obras/sales/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_sales_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        sale = get_sales(db, id)
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale no encontrado")
        return templates.TemplateResponse("app_obras/sales/edit.html", {
            "request": request,
            "sale": sale
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
