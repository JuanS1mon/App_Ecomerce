#!/usr/bin/env python3
"""
Versión simplificada de main.py para debugging
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Ecommerce Debug API",
    description="Versión simplificada para debugging",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar y registrar solo el router de ecommerce
try:
    from routers.ecommerce_auth import router as ecommerce_auth_router
    app.include_router(ecommerce_auth_router)
    logger.info("✅ Router de ecommerce registrado")
except Exception as e:
    logger.error(f"❌ Error al registrar router de ecommerce: {e}")

@app.get("/")
async def root():
    return {"message": "Ecommerce Debug API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor simplificado")
    uvicorn.run(
        app=app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )