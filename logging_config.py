import logging
import logging.config
import logging.handlers
import os

# Configuración de logging centralizada
LOG_FILE_PATH = os.path.join("logs", "server.log")

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
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "uvicorn": {"handlers": ["default", "file"], "level": "DEBUG"},
        "uvicorn.error": {"handlers": ["default", "file"], "level": "DEBUG"},
        "uvicorn.access": {"handlers": ["access", "file"], "level": "DEBUG", "propagate": False},
        "main": {"handlers": ["default", "file"], "level": "DEBUG"},
        "fastapi": {"handlers": ["default", "file"], "level": "DEBUG"},
    },
}

LOG_CONFIG = LOGGING_CONFIG  # Alias para compatibilidad con main.py y otros módulos

def setup_logging():
    # Asegurar que exista el directorio de logs
    try:
        logs_dir = os.path.dirname(LOG_FILE_PATH)
        if logs_dir and not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
    except Exception:
        pass

    logging.config.dictConfig(LOGGING_CONFIG)
