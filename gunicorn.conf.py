import multiprocessing
import os

# Bind
bind = "0.0.0.0:8000"

# Workers
workers = int(os.getenv("WORKERS", "4"))
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout
timeout = 600
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Graceful timeout
graceful_timeout = 30

# Max requests
max_requests = 1000
max_requests_jitter = 50

# Process naming
proc_name = "ecommerce_app"
