"""
Configuración específica para Core Service
"""
import os
from typing import List

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./core.db")

# JWT y Seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "core-service-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
ALLOWED_ORIGINS: List[str] = ["*"]

# Email
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "admin@empresa.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

# URLs de otros servicios
STOCK_SERVICE_URL = os.getenv("STOCK_SERVICE_URL", "http://stock-service:8002")
OBRAS_SERVICE_URL = os.getenv("OBRAS_SERVICE_URL", "http://obras-service:8003")
