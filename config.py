import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET", "default-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION", "30"))

# Configuración de la aplicación
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BASE_URL = FRONTEND_URL  # Alias para compatibilidad retroactiva
ORIGINS = os.getenv("ORIGINS", "*").split(",")
STATIC_DIR = os.getenv("STATIC_DIR", "sql_app/static")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

SECRET = SECRET_KEY  # Alias para compatibilidad retroactiva