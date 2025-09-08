"""
Configuración específica para Obras Service
"""
import os

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./obras.db")

# URLs de servicios
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-service:8001")

# Configuración específica de obras
PROJECT_STATUS_OPTIONS = ["planificacion", "en_progreso", "pausado", "completado"]
TASK_PRIORITY_OPTIONS = ["baja", "normal", "alta", "urgente"]
