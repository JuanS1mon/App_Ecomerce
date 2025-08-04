# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session
from datetime import date

# Imports del proyecto
from ....db.database import get_db
from .model_exhibitions import Exhibitions as ExhibitionsModel
from .schema_exhibitions import ExhibitionsCreate, ExhibitionsUpdate, ExhibitionsRead
from .service_exhibitions import (
    create_exhibitions, get_exhibitions, get_all_exhibitions, 
    delete_exhibitions, update_exhibitions, get_exhibitions_by_artwork, 
    get_exhibitions_by_institution, get_current_exhibitions, search_exhibitions_by_name
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/exhibitions",
    tags=["exhibitions"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ExhibitionsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_exhibitions(exhibitions: ExhibitionsCreate, db: Session = Depends(get_db)):
    if not exhibitions.name or not exhibitions.artwork_id or not exhibitions.institution_id:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos name, artwork_id e institution_id son obligatorios")
    try:
        exhibitions_model = ExhibitionsModel(**exhibitions.model_dump())
        db_exhibitions = create_exhibitions(db=db, exhibitions=exhibitions_model)
        return ExhibitionsRead.model_validate(db_exhibitions)
    except Exception as e:
        logger.error(f"Error al crear Exhibitions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=ExhibitionsRead)
async def routes_get_exhibitions_id(id: int, db: Session = Depends(get_db)):
    try:
        db_exhibitions = get_exhibitions(db, id)
        if not db_exhibitions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitions no encontrado")
        return ExhibitionsRead.model_validate(db_exhibitions)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Exhibitions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[ExhibitionsRead])
async def routes_get_all_exhibitions(
    skip: int = 0, 
    limit: int = 100, 
    artwork_id: Optional[int] = Query(None),
    institution_id: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    current_only: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    try:
        if current_only:
            db_exhibitions = get_current_exhibitions(db)
        elif artwork_id:
            db_exhibitions = get_exhibitions_by_artwork(db, artwork_id)
        elif institution_id:
            db_exhibitions = get_exhibitions_by_institution(db, institution_id)
        elif name:
            db_exhibitions = search_exhibitions_by_name(db, name)
        else:
            db_exhibitions = get_all_exhibitions(db, skip=skip, limit=limit)
        
        return [ExhibitionsRead.model_validate(exhibition) for exhibition in db_exhibitions]
    except Exception as e:
        logger.error(f"Error al obtener lista de Exhibitions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_exhibitions(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_exhibitions(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitions no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Exhibitions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.put("/id/{id}", response_model=ExhibitionsRead)
async def routes_update_exhibitions(id: int, exhibitions: ExhibitionsUpdate, db: Session = Depends(get_db)):
    try:
        db_exhibitions = update_exhibitions(db, id, exhibitions)
        if not db_exhibitions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitions no encontrado")
        return ExhibitionsRead.model_validate(db_exhibitions)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Exhibitions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

# Endpoints especiales
@router.get("/current/", response_model=List[ExhibitionsRead])
async def routes_get_current_exhibitions(db: Session = Depends(get_db)):
    """Obtener exhibiciones actualmente en curso"""
    try:
        db_exhibitions = get_current_exhibitions(db)
        return [ExhibitionsRead.model_validate(exhibition) for exhibition in db_exhibitions]
    except Exception as e:
        logger.error(f"Error al obtener exhibiciones actuales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener exhibiciones actuales.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_exhibitions_html(request: Request, db: Session = Depends(get_db)):
    try:
        exhibitions = get_all_exhibitions(db)
        return templates.TemplateResponse("exhibitions/list.html", {
            "request": request,
            "exhibitions": exhibitions
        })
    except Exception as e:
        logger.error(f"Error al cargar página de exhibitions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_exhibitions_html(request: Request):
    return templates.TemplateResponse("exhibitions/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_exhibitions_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        exhibition = get_exhibitions(db, id)
        if not exhibition:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibition no encontrado")
        return templates.TemplateResponse("exhibitions/edit.html", {
            "request": request,
            "exhibition": exhibition
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
