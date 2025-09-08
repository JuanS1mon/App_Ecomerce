# Archivo de configuración de rutas para el módulo clientes

from fastapi import APIRouter
from .clientes import router as clientes_router

router = APIRouter()
router.include_router(clientes_router, prefix='/clientes', tags=['clientes'])
