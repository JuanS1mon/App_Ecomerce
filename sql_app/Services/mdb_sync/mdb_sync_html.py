from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Definir el router
router = APIRouter(
    tags=["MDB Sync HTML"],
    responses={404: {"description": "No encontrado"}},
)

# Configurar el directorio de plantillas
# La ruta base donde se buscarán las plantillas HTML
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "static" / "html"))

@router.get("/mdb-sync", response_class=HTMLResponse)
async def get_mdb_sync_page(
    request: Request,
):
    """
    Página para la sincronización de datos con archivos MDB (Microsoft Access)
    """
    return templates.TemplateResponse("mdb_sync/mdb_sync.html", {"request": request})