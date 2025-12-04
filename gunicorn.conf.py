import multiprocessing
import sys
import os

# ============================================================================
# LIMPIEZA CRÍTICA: Remover /agents/python ANTES de cualquier import
# ============================================================================

# 1. Limpiar PYTHONPATH
if 'PYTHONPATH' in os.environ:
    original = os.environ['PYTHONPATH']
    paths = [p for p in original.split(':') if p and '/agents/python' not in p]
    os.environ['PYTHONPATH'] = ':'.join(paths)
    print(f"[CONFIG] PYTHONPATH limpiado: {original} -> {os.environ['PYTHONPATH']}")

# 2. Limpiar sys.path INMEDIATAMENTE
original_syspath = sys.path.copy()
sys.path = [p for p in sys.path if '/agents/python' not in p]
print(f"[CONFIG] sys.path limpiado: {len(original_syspath)} -> {len(sys.path)} rutas")

# 3. CRÍTICO: Invalidar el caché de importación de Python
# Esto fuerza a Python a recargar módulos desde las rutas correctas
if hasattr(sys, 'path_importer_cache'):
    # Eliminar entradas que apunten a /agents/python
    keys_to_remove = [k for k in sys.path_importer_cache.keys() if isinstance(k, str) and '/agents/python' in k]
    for key in keys_to_remove:
        del sys.path_importer_cache[key]
    print(f"[CONFIG] Caché de importación limpiado: {len(keys_to_remove)} entradas removidas")

# 4. Eliminar typing_extensions del caché de módulos si ya fue importado
if 'typing_extensions' in sys.modules:
    print("[CONFIG] WARNING: typing_extensions ya estaba en sys.modules, removiéndolo...")
    del sys.modules['typing_extensions']

# ============================================================================
# HOOKS DE GUNICORN para asegurar limpieza en workers
# ============================================================================

def when_ready(server):
    """Se ejecuta cuando Gunicorn está listo pero antes de cargar workers"""
    print("[GUNICORN] Hook when_ready ejecutado")

def pre_fork(server, worker):
    """Se ejecuta ANTES de hacer fork de cada worker - CRÍTICO para limpieza"""
    # Limpiar sys.path
    sys.path = [p for p in sys.path if '/agents/python' not in p]
    
    # Limpiar caché de importación
    if hasattr(sys, 'path_importer_cache'):
        keys_to_remove = [k for k in sys.path_importer_cache.keys() 
                         if isinstance(k, str) and '/agents/python' in k]
        for key in keys_to_remove:
            del sys.path_importer_cache[key]
    
    # Eliminar typing_extensions si existe en caché
    if 'typing_extensions' in sys.modules:
        del sys.modules['typing_extensions']
    
    print(f"[WORKER PRE-FORK] Limpieza completa: sys.path={len(sys.path)} rutas")

# ============================================================================
# CONFIGURACIÓN DE GUNICORN
# ============================================================================

# Gestión de memoria y reciclaje de workers
max_requests = 1000
max_requests_jitter = 50

# Logging
log_file = "-"

# Configuración del servidor - Azure asigna el puerto automáticamente
# Usa la variable de entorno PORT si está presente (App Service)
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"
timeout = 230

# Workers dinámicos basados en CPU
num_cpus = multiprocessing.cpu_count()
workers = (num_cpus * 2) + 1

# Worker class para ASGI (FastAPI) - NO usar gthread
worker_class = "uvicorn.workers.UvicornWorker"
