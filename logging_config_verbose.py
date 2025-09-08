import logging
import logging.config
import logging.handlers
import os

# Configuración de logging ULTRA VERBOSA para debugging
LOG_FILE_PATH = os.path.join("logs", "server.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "ultra_verbose": {
            "format": "🔍 %(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
        },
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        },
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "format": "🌐 ACCESS: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "formatter": "ultra_verbose",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "DEBUG"
        },
        "access_console": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "DEBUG"
        },
        "file": {
            "formatter": "ultra_verbose",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": "DEBUG"
        }
    },
    "loggers": {
        # Root logger - captura TODO A NIVEL DEBUG
        "": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        
        # Uvicorn - servidor web MUY VERBOSO
        "uvicorn": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "uvicorn.error": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "uvicorn.access": {"handlers": ["access_console", "file"], "level": "DEBUG", "propagate": False},
        
        # FastAPI y aplicación MUY VERBOSO
        "fastapi": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "main": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        
        # Generador - ULTRA VERBOSO
        "generator": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "generator.main": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        
        # SQLAlchemy - ver TODAS las queries
        "sqlalchemy": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "sqlalchemy.engine": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "sqlalchemy.pool": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        
        # Requests HTTP - ver TODAS las peticiones
        "httpx": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        "requests": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        
        # Aplicación específica MUY VERBOSO
        "sql_app": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        
        # Python interno - capturar warnings
        "py.warnings": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}

LOG_CONFIG = LOGGING_CONFIG  # Alias para compatibilidad

def setup_logging():
    """Configurar logging ULTRA VERBOSO para debugging completo"""
    # Asegurar que exista el directorio de logs
    try:
        logs_dir = os.path.dirname(LOG_FILE_PATH)
        if logs_dir and not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creando directorio de logs: {e}")

    # Aplicar configuración de logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Forzar nivel DEBUG para el root logger
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Asegurar que todos los loggers principales estén en DEBUG
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi", "main", "generator", "sql_app"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    print("🔍 LOGGING ULTRA VERBOSO ACTIVADO - Todos los mensajes aparecerán en consola")

def log_request_response(request_info: str, response_info: str):
    """Helper para loggear requests y responses"""
    logger = logging.getLogger("http_debug")
    logger.debug(f"📤 REQUEST: {request_info}")
    logger.debug(f"📥 RESPONSE: {response_info}")

# Para uso directo desde otros módulos
def get_verbose_logger(name: str):
    """Obtener un logger ultra verboso"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
