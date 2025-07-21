import logging
import logging.config
from sql_app.config import ENVIRONMENT

# Configuración de logging optimizada para producción/desarrollo
def get_log_level():
    """Determina el nivel de log según el entorno"""
    if ENVIRONMENT == "production":
        return "INFO"
    elif ENVIRONMENT == "development":
        return "DEBUG"
    else:
        return "INFO"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "development": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "production" if ENVIRONMENT == "production" else "development",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": get_log_level()},
        "uvicorn.error": {"level": "ERROR"},
        "uvicorn.access": {"handlers": ["access"], "level": get_log_level(), "propagate": False},
        "main": {"handlers": ["default"], "level": get_log_level()},
        "fastapi": {"handlers": ["default"], "level": get_log_level()},
        "sqlalchemy.engine": {"handlers": ["default"], "level": "WARNING"},  # Reducir logs de SQL
    },
}
LOG_CONFIG = LOGGING_CONFIG  # Alias para compatibilidad con main.py y otros módulos

def setup_logging():
    """Configura el sistema de logging"""
    logging.config.dictConfig(LOGGING_CONFIG)
