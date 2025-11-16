import multiprocessing
import sys
import os

# ============================================================================
# HOOKS DE GUNICORN para limpiar PYTHONPATH en el momento correcto
# ============================================================================

def when_ready(server):
    """Se ejecuta cuando Gunicorn está listo pero antes de cargar workers"""
    print("[GUNICORN] Limpiando PYTHONPATH antes de cargar workers...")
    if 'PYTHONPATH' in os.environ:
        original = os.environ['PYTHONPATH']
        paths = original.split(':')
        # CRÍTICO: Remover /agents/python que tiene paquetes viejos de Azure
        filtered = [p for p in paths if p and '/agents/python' not in p]
        os.environ['PYTHONPATH'] = ':'.join(filtered)
        print(f"[GUNICORN] PYTHONPATH original: {original}")
        print(f"[GUNICORN] PYTHONPATH limpio: {os.environ['PYTHONPATH']}")

def pre_fork(server, worker):
    """Se ejecuta antes de hacer fork de cada worker"""
    # Limpiar sys.path también
    sys.path = [p for p in sys.path if '/agents/python' not in p]

# ============================================================================
# CONFIGURACIÓN DE GUNICORN
# ============================================================================

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
