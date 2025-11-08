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
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "format": "🌐 ACCESS: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "DEBUG"
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "DEBUG"
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": LOG_FILE_PATH,
            "encoding": "utf-8",
            "level": "DEBUG"
        }
    },
    "loggers": {
        # Capturar con nivel INFO (menos verboso)
        "uvicorn": {"handlers": ["default", "file"], "level": "INFO"},
        "uvicorn.error": {"handlers": ["default", "file"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["access", "file"], "level": "INFO", "propagate": False},
        "main": {"handlers": ["default", "file"], "level": "INFO"},
        "fastapi": {"handlers": ["default", "file"], "level": "INFO"},
        "generator": {"handlers": ["default", "file"], "level": "INFO"},
        "sql_app": {"handlers": ["default", "file"], "level": "INFO"},
        "Services": {"handlers": ["default", "file"], "level": "DEBUG"},  # DEBUG para servicios generados
        "Services": {"handlers": ["default", "file"], "level": "DEBUG"},  # DEBUG para servicios generados
        "sqlalchemy": {"handlers": ["default", "file"], "level": "WARNING"},  # Menos verboso
        "sqlalchemy.engine": {"handlers": ["default", "file"], "level": "WARNING"},  # Menos verboso
        "sqlalchemy.pool": {"handlers": ["default", "file"], "level": "WARNING"},  # Menos verboso
        "sqlalchemy.orm": {"handlers": ["default", "file"], "level": "WARNING"},  # Menos verboso
        "passlib": {"handlers": ["default", "file"], "level": "WARNING"},  # Menos verboso
    },
    "root": {
        "level": "INFO",
        "handlers": ["default", "file"]
    }
}

LOG_CONFIG = LOGGING_CONFIG  # Alias para compatibilidad

def setup_logging():
    # Asegurar que exista el directorio de logs
    try:
        logs_dir = os.path.dirname(LOG_FILE_PATH)
        if logs_dir and not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
    except Exception:
        pass

    logging.config.dictConfig(LOGGING_CONFIG)
    
    # NIVEL INFO PARA PRODUCCIÓN (menos verboso que DEBUG)
    logging.getLogger().setLevel(logging.INFO)
    print("[OK] Logging inicializado correctamente")
#Force reload
