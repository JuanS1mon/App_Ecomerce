# ============================================================================
# SISTEMA DE SQL_APP - MAIN TEST APPLICATION
# ============================================================================
# Archivo de prueba minimal para identificar problemas de estabilidad

import logging
import sys
import traceback

# Configurar logging básico
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from contextlib import asynccontextmanager
    import os

    logger.info("✅ Imports básicos exitosos")

    # Probar imports de routers
    try:
        from routers import usuarios as aut_usuario
        from routers import auth as auth_router
        from routers.config import configDB, Analisis, usuarios_admin
        from routers.config.Admin import router as admin_router
        logger.info("✅ Imports de routers exitosos")
    except Exception as e:
        logger.error(f"❌ Error importando routers: {e}")
        import traceback
        traceback.print_exc()

    logger.info("✅ Todos los imports exitosos")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("🚀 Iniciando aplicación en lifespan")
        # Startup logic
        try:
            # Probar creación de base de datos y tablas
            from db.database import create_database, create_tables
            from init_app import create_all_tables
            create_database()
            create_all_tables(create_tables, logger)
            logger.info("🗄️ Base de datos y tablas creadas")
        except Exception as e:
            logger.error(f"❌ Error en BD/tablas: {e}")
            import traceback
            traceback.print_exc()

        logger.info("✅ Startup logic completado")

        yield

        # Shutdown logic
        logger.info("🛑 Cerrando aplicación en lifespan")

    app = FastAPI(
        title="Test API",
        description="API de prueba",
        version="1.0.0",
        lifespan=lifespan
    )

    # Configurar archivos estáticos
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Middlewares
    try:
        from fastapi.middleware.cors import CORSMiddleware
        from app_settings import CORS_CONFIG
        app.add_middleware(
            CORSMiddleware,
            allow_origins=CORS_CONFIG["allow_origins"],
            allow_credentials=CORS_CONFIG["allow_credentials"],
            allow_methods=CORS_CONFIG["allow_methods"],
            allow_headers=CORS_CONFIG["allow_headers"],
        )
        logger.info("✅ Middleware CORS agregado")
    except Exception as e:
        logger.error(f"❌ Error agregando CORS: {e}")
        import traceback
        traceback.print_exc()

    # Incluir routers
    try:
        app.include_router(aut_usuario.router)
        app.include_router(aut_usuario.usuarios_router)
        app.include_router(auth_router.router)
        app.include_router(usuarios_admin.router)
        app.include_router(configDB.router)
        app.include_router(admin_router)
        logger.info("✅ Routers incluidos exitosamente")
    except Exception as e:
        logger.error(f"❌ Error incluyendo routers: {e}")
        import traceback
        traceback.print_exc()

    @app.get("/")
    async def root():
        logger.info("📄 Solicitud a raíz")
        return {"message": "Servidor de prueba funcionando"}

    @app.get("/test")
    async def test():
        logger.info("🧪 Solicitud a test")
        return {"status": "ok"}

    logger.info("✅ Aplicación FastAPI creada")

    if __name__ == "__main__":
        import uvicorn
        logger.info("🚀 Iniciando servidor de prueba...")
        try:
            uvicorn.run(
                app=app,
                host="127.0.0.1",
                port=8001,
                reload=False,
                log_level="debug",
                access_log=True
            )
            logger.info("✅ uvicorn.run() terminó normalmente")
        except KeyboardInterrupt:
            logger.info("🛑 Servidor detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error al iniciar servidor: {str(e)}")
            logger.error("Traceback completo:")
            traceback.print_exc()
        finally:
            logger.info("🔚 Bloque finally ejecutado")

except Exception as e:
    logger.error(f"❌ Error general: {str(e)}")
    traceback.print_exc()