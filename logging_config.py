import logging

# Configuración de logging centralizada
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            # Formato seguro para logs de acceso de Uvicorn
            "format": "%(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
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
        "uvicorn": {"handlers": ["default"], "level": "DEBUG"},
        "uvicorn.error": {"level": "DEBUG"},
        "uvicorn.access": {"handlers": ["access"], "level": "DEBUG", "propagate": False},
        "main": {"handlers": ["default"], "level": "DEBUG"},
        "fastapi": {"handlers": ["default"], "level": "DEBUG"},
    },
}

LOG_CONFIG = LOGGING_CONFIG  # Alias para compatibilidad con main.py y otros módulos

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
