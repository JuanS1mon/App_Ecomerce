# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional

# Imports del proyecto
from ....db.database import get_db
from .model_artworks import Artworks as ArtworksModel
from .schema_artworks import ArtworksCreate, ArtworksUpdate, ArtworksRead
from .service_artworks import (
    create_artworks, get_artworks, get_all_artworks, delete_artworks, update_artworks,
    get_artworks_by_artist, get_artworks_by_inventory_code, get_available_artworks
)

import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/artworks",
    tags=["artworks"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ArtworksRead, status_code=status.HTTP_201_CREATED)
async def routes_post_artworks(artworks: ArtworksCreate, db: Session = Depends(get_db)):
    if not artworks.inventory_code or not artworks.title:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos inventory_code y title son obligatorios")
    try:
        artworks_model = ArtworksModel(**artworks.model_dump())
        db_artworks = create_artworks(db=db, artworks=artworks_model)
        return ArtworksRead.model_validate(db_artworks)
    except Exception as e:
        logger.error(f"Error al crear Artwork: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=ArtworksRead)
async def routes_get_artworks_id(id: int, db: Session = Depends(get_db)):
    try:
        db_artworks = get_artworks(db, id)
        if not db_artworks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork no encontrado")
        return ArtworksRead.model_validate(db_artworks)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Artwork: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/inventory/{inventory_code}", response_model=ArtworksRead)
async def routes_get_artworks_by_inventory(inventory_code: str, db: Session = Depends(get_db)):
    try:
        db_artworks = get_artworks_by_inventory_code(db, inventory_code)
        if not db_artworks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork no encontrado")
        return ArtworksRead.model_validate(db_artworks)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Artwork por código: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[ArtworksRead])
async def routes_get_all_artworks(
    skip: int = 0, 
    limit: int = 100, 
    artist_id: Optional[int] = Query(None),
    is_available: Optional[bool] = Query(None),
    is_sold: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if artist_id:
            db_artworks = get_artworks_by_artist(db, artist_id, skip, limit)
        elif is_available is not None:
            db_artworks = get_available_artworks(db, is_available, skip, limit)
        else:
            db_artworks = get_all_artworks(db, skip=skip, limit=limit)
        
        return [ArtworksRead.model_validate(artwork) for artwork in db_artworks]
    except Exception as e:
        logger.error(f"Error al obtener lista de Artworks: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.put("/id/{id}", response_model=ArtworksRead)
async def routes_put_artworks(id: int, artworks: ArtworksUpdate, db: Session = Depends(get_db)):
    try:
        db_artworks = update_artworks(db, id, artworks)
        if not db_artworks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork no encontrado")
        return ArtworksRead.model_validate(db_artworks)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Artwork: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_artworks(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_artworks(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Artwork: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_artworks_html(request: Request, db: Session = Depends(get_db)):
    try:
        artworks = get_all_artworks(db)
        return templates.TemplateResponse("artworks/list.html", {
            "request": request,
            "artworks": artworks
        })
    except Exception as e:
        logger.error(f"Error al cargar página de artworks: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_artworks_html(request: Request, db: Session = Depends(get_db)):
    # Aquí podrías cargar artistas y estados para los select
    return templates.TemplateResponse("artworks/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_artworks_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        artwork = get_artworks(db, id)
        if not artwork:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork no encontrado")
        return templates.TemplateResponse("artworks/edit.html", {
            "request": request,
            "artwork": artwork
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
