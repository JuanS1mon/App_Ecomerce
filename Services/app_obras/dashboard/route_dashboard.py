# Imports necesarios
from datetime import date, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

# Imports del proyecto
from ....db.database import get_db
from ..artists.service_artists import get_all_artists
from ..artworks.service_artworks import get_all_artworks, get_available_artworks
from ..artwork_states.service_artwork_states import get_all_artwork_states
from ..locations.service_locations import get_all_locations
from ..institutions.service_institutions import get_all_institutions
from ..exhibitions.service_exhibitions import get_all_exhibitions, get_current_exhibitions
from ..sales.service_sales import get_all_sales, get_pending_payments, get_sales_by_year
from ..documents.service_documents import get_all_documents, get_document_types_summary

import logging

logger = logging.getLogger(__name__)

# Definir la instancia de Jinja2Templates
templates = Jinja2Templates(directory="sql_app/static")

# Definir el router directamente
router = APIRouter(
    include_in_schema=False,
    prefix="/dashboard",
    tags=["Dashboard Obras"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "Ruta no encontrada"}}
)

# Agregar también un router sin prefijo para ruta principal
main_router = APIRouter(
    include_in_schema=False,
    tags=["Dashboard Obras Principal"]
)

@main_router.get("/obras", response_class=HTMLResponse)
@main_router.get("/obras/", response_class=HTMLResponse)
async def obras_main_redirect():
    """
    Redirección desde /app_obras/obras al dashboard
    """
    return RedirectResponse(url="/app_obras/dashboard", status_code=302)

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def obras_dashboard(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Dashboard principal del sistema de obras de arte
    """
    try:
        # Obtener estadísticas generales
        artists_count = len(get_all_artists(db))
        artworks_count = len(get_all_artworks(db))
        available_artworks = len(get_available_artworks(db, True))
        sold_artworks = len([artwork for artwork in get_all_artworks(db) if artwork.is_sold])
        
        locations_count = len(get_all_locations(db))
        institutions_count = len(get_all_institutions(db))
        exhibitions_count = len(get_all_exhibitions(db))
        current_exhibitions = len(get_current_exhibitions(db))
        
        sales_count = len(get_all_sales(db))
        pending_payments = len(get_pending_payments(db))
        documents_count = len(get_all_documents(db))
        
        # Obtener resumen de documentos por tipo
        document_types = get_document_types_summary(db)
        
        # Calcular estadísticas de ventas del año actual
        current_year = date.today().year
        current_year_sales = get_sales_by_year(db, current_year)
        total_sales_value = sum(float(sale.real_value) for sale in current_year_sales) if current_year_sales else 0
        
        # Datos para la template
        template_data = {
            "request": request,
            "page_title": "Dashboard - Sistema de Obras de Arte",
            "current_date": date.today().strftime("%d de %B, %Y"),
            
            # Estadísticas principales
            "stats": {
                "artists_count": artists_count,
                "artworks_count": artworks_count,
                "available_artworks": available_artworks,
                "sold_artworks": sold_artworks,
                "locations_count": locations_count,
                "institutions_count": institutions_count,
                "exhibitions_count": exhibitions_count,
                "current_exhibitions": current_exhibitions,
                "sales_count": sales_count,
                "pending_payments": pending_payments,
                "documents_count": documents_count,
                "total_sales_value": total_sales_value,
                "current_year": current_year
            },
            
            # Datos adicionales
            "document_types": document_types,
            "availability_rate": round((available_artworks / artworks_count * 100), 1) if artworks_count > 0 else 0,
            "sales_rate": round((sold_artworks / artworks_count * 100), 1) if artworks_count > 0 else 0,
        }
        
        logger.info(f"Dashboard cargado con {artworks_count} obras y {artists_count} artistas")
        return templates.TemplateResponse("obras_dashboard.html", template_data)
        
    except Exception as e:
        logger.error(f"Error en dashboard de obras: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al cargar dashboard: {str(e)}"
        )

@router.get("/api/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    API para obtener estadísticas del dashboard en formato JSON
    """
    try:
        # Obtener todas las estadísticas
        artists_count = len(get_all_artists(db))
        artworks_count = len(get_all_artworks(db))
        available_artworks = len(get_available_artworks(db, True))
        sold_artworks = len([artwork for artwork in get_all_artworks(db) if artwork.is_sold])
        
        sales_count = len(get_all_sales(db))
        exhibitions_count = len(get_all_exhibitions(db))
        current_exhibitions = len(get_current_exhibitions(db))
        
        # Calcular valores de ventas
        current_year = date.today().year
        current_year_sales = get_sales_by_year(db, current_year)
        total_sales_value = sum(float(sale.real_value) for sale in current_year_sales) if current_year_sales else 0
        
        return {
            "success": True,
            "data": {
                "artists_count": artists_count,
                "artworks_count": artworks_count,
                "available_artworks": available_artworks,
                "sold_artworks": sold_artworks,
                "sales_count": sales_count,
                "exhibitions_count": exhibitions_count,
                "current_exhibitions": current_exhibitions,
                "total_sales_value": total_sales_value,
                "availability_rate": round((available_artworks / artworks_count * 100), 1) if artworks_count > 0 else 0,
                "sales_rate": round((sold_artworks / artworks_count * 100), 1) if artworks_count > 0 else 0,
                "current_year": current_year
            }
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/api/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """
    API para obtener actividad reciente del sistema
    """
    try:
        # Obtener obras recientes (últimas 10)
        recent_artworks = get_all_artworks(db, skip=0, limit=10)
        
        # Obtener exhibiciones actuales
        current_exhibitions = get_current_exhibitions(db)
        
        # Obtener pagos pendientes
        pending_payments = get_pending_payments(db)
        
        return {
            "success": True,
            "data": {
                "recent_artworks": [
                    {
                        "id": artwork.id,
                        "title": artwork.title,
                        "inventory_code": artwork.inventory_code,
                        "artist_id": artwork.artist_id
                    } for artwork in recent_artworks
                ],
                "current_exhibitions": [
                    {
                        "id": exhibition.id,
                        "name": exhibition.name,
                        "start_date": exhibition.start_date.isoformat(),
                        "end_date": exhibition.end_date.isoformat()
                    } for exhibition in current_exhibitions
                ],
                "pending_payments_count": len(pending_payments)
            }
        }
    except Exception as e:
        logger.error(f"Error al obtener actividad reciente: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener actividad: {str(e)}")

# Exportar ambos routers para que puedan ser importados
__all__ = ["router", "main_router"]
