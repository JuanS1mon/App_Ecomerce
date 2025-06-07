# scraping.py
from io import BytesIO
import os
import logging
from fastapi import APIRouter, Request, status, Depends, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from ...Services.security.security import get_current_user
from ...db.database import get_db
from ...db.schemas.config.Usuarios import UserDB
from datetime import datetime
import json
from sqlalchemy.orm import Session
import pandas as pd
from pydantic import BaseModel
from ...db.schemas.Scraping import ScraperTestConfig
from ...Services.scraping.scraping import extract_with_beautifulsoup
from ...Services.scraping.scraping import extract_with_selenium

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ...db.models.config.activityLog import ActivityLog
 
# Configuración de logging
logging.basicConfig(
    filename='logs/scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ajustar el directorio de las plantillas
templates = Jinja2Templates(directory="sql_app/static")


router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
    prefix="/scraping",
    tags=["Scraping"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)


class ScrapingRequest(BaseModel):
    url: str
    selector: str = None
    max_pages: int = 1


@router.get("/admin")
async def scraping_admin(
    request: Request,
    current_user: UserDB = Depends(get_current_user)
):
    return templates.TemplateResponse("scraping/scraping_admin.html", {"request": request, "user": current_user})


@router.get("/nuevo")
async def scraping_admin(
    request: Request,
    current_user: UserDB = Depends(get_current_user)
):
    return templates.TemplateResponse("scraping/scraping_new.html", {"request": request, "user": current_user})

@router.post("/test-extraction", response_class=JSONResponse)
async def test_extraction(
    config: ScraperTestConfig,
    current_user: UserDB = Depends(get_current_user)
):
    try:
        # Registrar la actividad
        logging.info(f"Usuario {current_user.usuario} iniciando prueba de extracción: {config.url}")
        
        # Ejecutar la extracción según la tecnología seleccionada
        if config.technology == "beautifulsoup":
            results = extract_with_beautifulsoup(config)
        elif config.technology == "selenium":
            results = extract_with_selenium(config)
        #elif config.technology == "scrapy":
            #results = extract_with_scrapy(config)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Tecnología no soportada: {config.technology}"}
            )
            
        # Devolver los resultados
        return JSONResponse(
            content={
                "success": True,
                "message": "Extracción completada con éxito",
                "results": results,
                "count": len(results)
            }
        )
        
    except Exception as e:
        logging.error(f"Error en prueba de extracción: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Error al realizar la extracción"
            }
        )
@router.post("/debug-payload", response_class=JSONResponse)
async def debug_payload(payload: dict):
    """Endpoint para depurar la estructura JSON recibida"""
    return JSONResponse(
        content={
            "received": payload,
            "expected_structure": {
                "url": "string",
                "technology": "string (beautifulsoup, selenium, etc)",
                "selectors": [
                    {
                        "name": "string",
                        "path": "string",
                        "type": "string",
                        "attribute": "string (opcional)",
                        "multiple": "boolean"
                    }
                ],
                "container_selector": "string (opcional)",
                "request_delay": "integer",
                "request_timeout": "integer",
                "proxy": {
                    "enabled": "boolean",
                    "address": "string (opcional)",
                    "proxy_type": "string (opcional)"
                },
                "pagination": {
                    "enabled": "boolean",
                    "type": "string (opcional)",
                    "next_selector": "string (opcional)",
                    "page_parameter": "string (opcional)",
                    "max_pages": "integer",
                    "load_more_selector": "string (opcional)"
                },
                "javascript": {
                    "enabled": "boolean",
                    "code": "string (opcional)"
                }
            }
        }
    )