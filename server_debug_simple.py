#!/usr/bin/env python3
"""
Script de diagnóstico para ejecutar el servidor con logging detallado
"""
import sys
import os
import logging
import time

# Configurar logging muy detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server_debug.log')
    ]
)

logger = logging.getLogger(__name__)
logger.info("Iniciando script de diagnostico del servidor")

try:
    # Importar la aplicación
    logger.info("Importando aplicacion...")
    import main
    logger.info("Aplicacion importada correctamente")

    # Verificar que la app existe
    if hasattr(main, 'app'):
        logger.info("Variable 'app' encontrada en main.py")
    else:
        logger.error("Variable 'app' NO encontrada en main.py")
        sys.exit(1)

    # Ejecutar el servidor usando uvicorn.run()
    logger.info("Ejecutando uvicorn.run()...")
    import uvicorn

    # Configuración de uvicorn con logging detallado
    config = uvicorn.Config(
        app=main.app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="debug",
        access_log=True,
        use_colors=True,
    )

    server = uvicorn.Server(config)

    # Ejecutar el servidor
    logger.info("Iniciando servidor...")
    server.run()

except KeyboardInterrupt:
    logger.info("Servidor detenido por KeyboardInterrupt")
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    logger.info("Script terminado")