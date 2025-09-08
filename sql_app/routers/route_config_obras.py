# Archivo de configuración de rutas para el módulo obras

from fastapi import APIRouter
from .obras import router as obras_router

router = APIRouter()
router.include_router(obras_router, prefix='/obras', tags=['obras'])
