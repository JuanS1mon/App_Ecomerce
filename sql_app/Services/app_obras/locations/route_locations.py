# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session

# Imports del proyecto
from ....db.database import get_db
from .model_locations import Locations as LocationsModel
from .schema_locations import LocationsCreate, LocationsUpdate, LocationsRead
from .service_locations import (
    create_locations, get_locations, get_all_locations, 
    delete_locations, update_locations, get_locations_by_city, get_locations_by_country
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=LocationsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_locations(locations: LocationsCreate, db: Session = Depends(get_db)):
    if not locations.name or not locations.city or not locations.country:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos name, city y country son obligatorios")
    try:
        locations_model = LocationsModel(**locations.model_dump())
        db_locations = create_locations(db=db, locations=locations_model)
        return LocationsRead.model_validate(db_locations)
    except Exception as e:
        logger.error(f"Error al crear Locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=LocationsRead)
async def routes_get_locations_id(id: int, db: Session = Depends(get_db)):
    try:
        db_locations = get_locations(db, id)
        if not db_locations:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locations no encontrado")
        return LocationsRead.model_validate(db_locations)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[LocationsRead])
async def routes_get_all_locations(
    skip: int = 0, 
    limit: int = 100, 
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if city:
            db_locations = get_locations_by_city(db, city)
        elif country:
            db_locations = get_locations_by_country(db, country)
        else:
            db_locations = get_all_locations(db, skip=skip, limit=limit)
        
        return [LocationsRead.model_validate(location) for location in db_locations]
    except Exception as e:
        logger.error(f"Error al obtener lista de Locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_locations(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_locations(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locations no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.put("/id/{id}", response_model=LocationsRead)
async def routes_update_locations(id: int, locations: LocationsUpdate, db: Session = Depends(get_db)):
    try:
        db_locations = update_locations(db, id, locations)
        if not db_locations:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locations no encontrado")
        return LocationsRead.model_validate(db_locations)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_locations_html(request: Request, db: Session = Depends(get_db)):
    try:
        locations = get_all_locations(db)
        return templates.TemplateResponse("app_obras/locations/list.html", {
            "request": request,
            "locations": locations
        })
    except Exception as e:
        logger.error(f"Error al cargar página de locations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_locations_html(request: Request):
    return templates.TemplateResponse("app_obras/locations/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_locations_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        location = get_locations(db, id)
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location no encontrado")
        return templates.TemplateResponse("app_obras/locations/edit.html", {
            "request": request,
            "location": location
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
