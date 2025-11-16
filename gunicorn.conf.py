import multiprocessing

# Gestión de memoria y reciclaje de workers
max_requests = 1000
max_requests_jitter = 50

# Logging
log_file = "-"

# Configuración del servidor
bind = "0.0.0.0"
timeout = 230

# Workers dinámicos basados en CPU
num_cpus = multiprocessing.cpu_count()
workers = (num_cpus * 2) + 1

# Worker class para ASGI (FastAPI)
worker_class = "uvicorn.workers.UvicornWorker"
