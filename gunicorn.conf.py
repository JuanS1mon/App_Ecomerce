import multiprocessing
import sys
import os

# Limpiar PYTHONPATH para evitar conflictos con paquetes del sistema Azure
# Mantener solo el directorio del entorno virtual
if 'PYTHONPATH' in os.environ:
    venv_paths = [p for p in os.environ['PYTHONPATH'].split(':') if 'antenv' in p or 'site-packages' in p]
    if venv_paths:
        os.environ['PYTHONPATH'] = ':'.join(venv_paths)

# Gestión de memoria y reciclaje de workers
max_requests = 1000
max_requests_jitter = 50

# Logging
log_file = "-"

# Configuración del servidor - Azure asigna el puerto automáticamente
bind = "0.0.0.0:8000"
timeout = 230

# Workers dinámicos basados en CPU
num_cpus = multiprocessing.cpu_count()
workers = (num_cpus * 2) + 1

# Worker class para ASGI (FastAPI) - NO usar gthread
worker_class = "uvicorn.workers.UvicornWorker"
