import uvicorn
from main import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Iniciando servidor en puerto 8001...')
try:
    uvicorn.run(app, host='0.0.0.0', port=8001, reload=False)
except Exception as e:
    logger.error(f'Error al iniciar servidor: {e}')