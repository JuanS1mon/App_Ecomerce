"""
Configuración específica para Stock Service
"""
import os

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock.db")

# URLs de servicios
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-service:8001")

# Configuración específica de stock
STOCK_CALCULATION_INTERVAL = int(os.getenv("STOCK_CALCULATION_INTERVAL", "60"))  # segundos
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))
