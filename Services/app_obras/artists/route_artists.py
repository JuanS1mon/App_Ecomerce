# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

# Imports del proyecto
from ....db.database import get_db
from .model_artists import Artists as ArtistsModel
from .schema_artists import ArtistsCreate, ArtistsUpdate, ArtistsRead
from .service_artists import (
    create_artists, get_artists, get_all_artists, delete_artists, update_artists
)

import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/artists",
    tags=["artists"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ArtistsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_artists(artists: ArtistsCreate, db: Session = Depends(get_db)):
    if artists.full_name is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo full_name es obligatorio")
    try:
        artists_model = ArtistsModel(**artists.model_dump())
        db_artists = create_artists(db=db, artists=artists_model)
        return ArtistsRead.model_validate(db_artists)
    except Exception as e:
        logger.error(f"Error al crear Artists: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=ArtistsRead)
async def routes_get_artists_id(id: int, db: Session = Depends(get_db)):
    try:
        db_artists = get_artists(db, id)
        if not db_artists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artists no encontrado")
        return ArtistsRead.model_validate(db_artists)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Artists: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[ArtistsRead])
async def routes_get_all_artists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        db_artists = get_all_artists(db, skip=skip, limit=limit)
        return [ArtistsRead.model_validate(artist) for artist in db_artists]
    except Exception as e:
        logger.error(f"Error al obtener lista de Artists: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.put("/id/{id}", response_model=ArtistsRead)
async def routes_put_artists(id: int, artists: ArtistsUpdate, db: Session = Depends(get_db)):
    try:
        db_artists = update_artists(db, id, artists)
        if not db_artists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artists no encontrado")
        return ArtistsRead.model_validate(db_artists)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Artists: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_artists(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_artists(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artists no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Artists: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_artists_html(request: Request, db: Session = Depends(get_db)):
    try:
        artists = get_all_artists(db)
        return templates.TemplateResponse("artists/list.html", {
            "request": request,
            "artists": artists
        })
    except Exception as e:
        logger.error(f"Error al cargar página de artists: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_artists_html(request: Request):
    return templates.TemplateResponse("artists/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_artists_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        artist = get_artists(db, id)
        if not artist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist no encontrado")
        return templates.TemplateResponse("artists/edit.html", {
            "request": request,
            "artist": artist
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
