# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

# Imports del proyecto
from ....db.database import get_db
from .model_artwork_states import ArtworkStates as ArtworkStatesModel
from .schema_artwork_states import ArtworkStatesCreate, ArtworkStatesUpdate, ArtworkStatesRead
from .service_artwork_states import (
    create_artwork_states, get_artwork_states, get_all_artwork_states, 
    delete_artwork_states, update_artwork_states
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/artwork_states",
    tags=["artwork_states"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ArtworkStatesRead, status_code=status.HTTP_201_CREATED)
async def routes_post_artwork_states(artwork_states: ArtworkStatesCreate, db: Session = Depends(get_db)):
    if artwork_states.description is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo description es obligatorio")
    try:
        artwork_states_model = ArtworkStatesModel(**artwork_states.model_dump())
        db_artwork_states = create_artwork_states(db=db, artwork_states=artwork_states_model)
        return ArtworkStatesRead.model_validate(db_artwork_states)
    except Exception as e:
        logger.error(f"Error al crear ArtworkStates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=ArtworkStatesRead)
async def routes_get_artwork_states_id(id: int, db: Session = Depends(get_db)):
    try:
        db_artwork_states = get_artwork_states(db, id)
        if not db_artwork_states:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ArtworkStates no encontrado")
        return ArtworkStatesRead.model_validate(db_artwork_states)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener ArtworkStates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[ArtworkStatesRead])
async def routes_get_all_artwork_states(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        db_artwork_states = get_all_artwork_states(db, skip=skip, limit=limit)
        return [ArtworkStatesRead.model_validate(state) for state in db_artwork_states]
    except Exception as e:
        logger.error(f"Error al obtener lista de ArtworkStates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_artwork_states(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_artwork_states(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ArtworkStates no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar ArtworkStates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.put("/id/{id}", response_model=ArtworkStatesRead)
async def routes_update_artwork_states(id: int, artwork_states: ArtworkStatesUpdate, db: Session = Depends(get_db)):
    try:
        db_artwork_states = update_artwork_states(db, id, artwork_states)
        if not db_artwork_states:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ArtworkStates no encontrado")
        return ArtworkStatesRead.model_validate(db_artwork_states)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar ArtworkStates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_artwork_states_html(request: Request, db: Session = Depends(get_db)):
    try:
        artwork_states = get_all_artwork_states(db)
        return templates.TemplateResponse("artwork_states/list.html", {
            "request": request,
            "artwork_states": artwork_states
        })
    except Exception as e:
        logger.error(f"Error al cargar página de artwork_states: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_artwork_states_html(request: Request):
    return templates.TemplateResponse("artwork_states/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_artwork_states_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        artwork_state = get_artwork_states(db, id)
        if not artwork_state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ArtworkState no encontrado")
        return templates.TemplateResponse("artwork_states/edit.html", {
            "request": request,
            "artwork_state": artwork_state
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
