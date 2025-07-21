# app_settings.py
# =============================
# Configuración centralizada de CORS y documentación de la API
# Este archivo permite modificar fácilmente los orígenes permitidos, credenciales, métodos y headers para CORS,
# así como las URLs de la documentación interactiva de FastAPI (Swagger y ReDoc).
# =============================

from sql_app.config import ORIGINS, ENVIRONMENT

# CORS_CONFIG:
# Diccionario con la configuración de CORS (Cross-Origin Resource Sharing).
# Configuración optimizada para producción vs desarrollo
def get_cors_config():
    if ENVIRONMENT == "production":
        # Configuración restrictiva para producción
        return {
            "allow_origins": ORIGINS if ORIGINS != ["*"] else [],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": [
                "Authorization", 
                "Content-Type", 
                "Accept", 
                "Origin", 
                "X-Requested-With",
                "X-CSRF-Token"
            ],
        }
    else:
        # Configuración permisiva para desarrollo
        return {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

CORS_CONFIG = get_cors_config()

# DOCS_URL y REDOC_URL:
# URLs para la documentación interactiva de la API.
# - DOCS_URL: Habilita/deshabilita la documentación Swagger (por defecto en /docs). Solo visible en desarrollo.
# - REDOC_URL: Habilita/deshabilita la documentación ReDoc (por defecto en /redoc). Solo visible en desarrollo.
# En producción, ambas quedan deshabilitadas por seguridad.
DOCS_URL = "/docs" if ENVIRONMENT == "development" else None
REDOC_URL = "/redoc" if ENVIRONMENT == "development" else None
