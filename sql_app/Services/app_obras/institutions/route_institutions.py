# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session

# Imports del proyecto
from ....db.database import get_db
from .model_institutions import Institutions as InstitutionsModel
from .schema_institutions import InstitutionsCreate, InstitutionsUpdate, InstitutionsRead
from .service_institutions import (
    create_institutions, get_institutions, get_all_institutions, 
    delete_institutions, update_institutions, get_institutions_by_location, search_institutions_by_name
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/institutions",
    tags=["institutions"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=InstitutionsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_institutions(institutions: InstitutionsCreate, db: Session = Depends(get_db)):
    if not institutions.name or not institutions.location_id:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos name y location_id son obligatorios")
    try:
        institutions_model = InstitutionsModel(**institutions.model_dump())
        db_institutions = create_institutions(db=db, institutions=institutions_model)
        return InstitutionsRead.model_validate(db_institutions)
    except Exception as e:
        logger.error(f"Error al crear Institutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=InstitutionsRead)
async def routes_get_institutions_id(id: int, db: Session = Depends(get_db)):
    try:
        db_institutions = get_institutions(db, id)
        if not db_institutions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institutions no encontrado")
        return InstitutionsRead.model_validate(db_institutions)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Institutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[InstitutionsRead])
async def routes_get_all_institutions(
    skip: int = 0, 
    limit: int = 100, 
    location_id: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if location_id:
            db_institutions = get_institutions_by_location(db, location_id)
        elif name:
            db_institutions = search_institutions_by_name(db, name)
        else:
            db_institutions = get_all_institutions(db, skip=skip, limit=limit)
        
        return [InstitutionsRead.model_validate(institution) for institution in db_institutions]
    except Exception as e:
        logger.error(f"Error al obtener lista de Institutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_institutions(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_institutions(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institutions no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Institutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.put("/id/{id}", response_model=InstitutionsRead)
async def routes_update_institutions(id: int, institutions: InstitutionsUpdate, db: Session = Depends(get_db)):
    try:
        db_institutions = update_institutions(db, id, institutions)
        if not db_institutions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institutions no encontrado")
        return InstitutionsRead.model_validate(db_institutions)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Institutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_institutions_html(request: Request, db: Session = Depends(get_db)):
    try:
        institutions = get_all_institutions(db)
        return templates.TemplateResponse("app_obras/institutions/list.html", {
            "request": request,
            "institutions": institutions
        })
    except Exception as e:
        logger.error(f"Error al cargar página de institutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_institutions_html(request: Request, db: Session = Depends(get_db)):
    try:
        # Importamos el servicio de locations
        from ..locations.service_locations import get_all_locations
        
        locations = get_all_locations(db)
        
        return templates.TemplateResponse("app_obras/institutions/create.html", {
            "request": request,
            "locations": locations
        })
    except Exception as e:
        logger.error(f"Error al cargar página de creación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_institutions_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        institution = get_institutions(db, id)
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution no encontrado")
        return templates.TemplateResponse("app_obras/institutions/edit.html", {
            "request": request,
            "institution": institution
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
