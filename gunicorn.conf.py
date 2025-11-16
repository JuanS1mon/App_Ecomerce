import multiprocessing
import sys
import os

# ============================================================================
# LIMPIEZA INMEDIATA del PYTHONPATH corrupto de Azure
# ============================================================================
# DEBE ejecutarse ANTES de cualquier import para evitar conflictos

if 'PYTHONPATH' in os.environ:
    original_pythonpath = os.environ['PYTHONPATH']
    paths = original_pythonpath.split(':')
    # Filtrar /agents/python que contiene typing_extensions.py obsoleto
    clean_paths = [p for p in paths if p and '/agents/python' not in p]
    os.environ['PYTHONPATH'] = ':'.join(clean_paths)
    print(f"[STARTUP] PYTHONPATH limpiado: {original_pythonpath} -> {os.environ['PYTHONPATH']}")

# Limpiar sys.path también para el proceso maestro
sys.path = [p for p in sys.path if '/agents/python' not in p]
print(f"[STARTUP] sys.path limpiado, rutas restantes: {len(sys.path)}")

# ============================================================================
# HOOKS DE GUNICORN para asegurar limpieza en workers
# ============================================================================

def when_ready(server):
    """Se ejecuta cuando Gunicorn está listo pero antes de cargar workers"""
    print("[GUNICORN] Hook when_ready: Verificando limpieza de PYTHONPATH...")

def pre_fork(server, worker):
    """Se ejecuta antes de hacer fork de cada worker"""
    # Doble verificación: limpiar sys.path en cada worker
    sys.path = [p for p in sys.path if '/agents/python' not in p]
    print(f"[WORKER] sys.path limpiado en worker, total paths: {len(sys.path)}")

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
