# =============================
# PROMETHEUS METRICS
# =============================
# Sistema de métricas para monitoreo con Prometheus

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
import time
import logging
from sql_app.config import ENVIRONMENT
from typing import Optional

logger = logging.getLogger("metrics")

# Registry personalizado para evitar conflictos
REGISTRY = CollectorRegistry()

# =============================
# MÉTRICAS DEFINIDAS
# =============================

# Contadores de peticiones HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

# Histograma de duración de peticiones
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Gauge para peticiones concurrentes
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    registry=REGISTRY
)

# Métricas de base de datos
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    registry=REGISTRY
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    registry=REGISTRY
)

# Métricas de cache
cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result'],
    registry=REGISTRY
)

# Métricas de autenticación
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result'],
    registry=REGISTRY
)

# Métricas de rate limiting
rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint'],
    registry=REGISTRY
)

# Métricas del sistema
system_uptime_seconds = Gauge(
    'system_uptime_seconds',
    'System uptime in seconds',
    registry=REGISTRY
)

# Métricas de errores
error_responses_total = Counter(
    'error_responses_total',
    'Total error responses',
    ['error_type', 'endpoint'],
    registry=REGISTRY
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para recopilar métricas de HTTP"""
    
    def __init__(self, app):
        super().__init__(app)
        self.start_time = time.time()
        
    async def dispatch(self, request: Request, call_next):
        # Incrementar peticiones en progreso
        http_requests_in_progress.inc()
        
        method = request.method
        path = self._normalize_path(request.url.path)
        
        # Medir tiempo de respuesta
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Registrar métricas
            duration = time.time() - start_time
            status_code = str(response.status_code)
            
            # Registrar petición
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            # Registrar duración
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Registrar errores si aplica
            if response.status_code >= 400:
                error_type = self._get_error_type(response.status_code)
                error_responses_total.labels(
                    error_type=error_type,
                    endpoint=path
                ).inc()
            
            return response
            
        except Exception as e:
            # Registrar excepción
            duration = time.time() - start_time
            
            error_responses_total.labels(
                error_type="exception",
                endpoint=path
            ).inc()
            
            logger.error(f"❌ Error en {method} {path}: {e}")
            raise
            
        finally:
            # Decrementar peticiones en progreso
            http_requests_in_progress.dec()
            
            # Actualizar uptime
            uptime = time.time() - self.start_time
            system_uptime_seconds.set(uptime)
    
    def _normalize_path(self, path: str) -> str:
        """Normaliza paths para evitar cardinalidad alta"""
        import re
        
        # Excluir endpoints de métricas
        if path == "/metrics":
            return path
            
        # Reemplazar IDs con placeholder
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Agrupar rutas similares
        if path.startswith('/api/'):
            return '/api/*'
        elif path.startswith('/static/'):
            return '/static/*'
        elif path.startswith('/admin/'):
            return '/admin/*'
        
        return path
    
    def _get_error_type(self, status_code: int) -> str:
        """Determina el tipo de error basado en el código de estado"""
        if 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown"

# =============================
# FUNCIONES DE UTILIDAD
# =============================

def record_cache_operation(operation: str, result: str):
    """Registra una operación de cache"""
    cache_operations_total.labels(
        operation=operation,
        result=result
    ).inc()

def record_auth_attempt(result: str):
    """Registra un intento de autenticación"""
    auth_attempts_total.labels(result=result).inc()

def record_rate_limit_hit(endpoint: str):
    """Registra un hit de rate limiting"""
    rate_limit_hits_total.labels(endpoint=endpoint).inc()

def record_db_query(query_type: str, duration: float):
    """Registra una query de base de datos"""
    db_query_duration_seconds.labels(query_type=query_type).observe(duration)

def update_db_connections(count: int):
    """Actualiza el número de conexiones activas de BD"""
    db_connections_active.set(count)

# =============================
# ENDPOINT DE MÉTRICAS
# =============================

async def metrics_endpoint():
    """Endpoint para exponer métricas a Prometheus"""
    try:
        metrics_data = generate_latest(REGISTRY)
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"❌ Error generando métricas: {e}")
        return Response(
            content="Error generating metrics",
            status_code=500
        )

# =============================
# DECORADORES PARA MÉTRICAS
# =============================

def track_db_query(query_type: str):
    """Decorador para trackear queries de BD"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                record_db_query(query_type, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                record_db_query(f"{query_type}_error", duration)
                raise
        return wrapper
    return decorator

def track_cache_operation(operation: str):
    """Decorador para trackear operaciones de cache"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                record_cache_operation(operation, "success")
                return result
            except Exception as e:
                record_cache_operation(operation, "error")
                raise
        return wrapper
    return decorator

# =============================
# INICIALIZACIÓN
# =============================

def init_metrics():
    """Inicializa el sistema de métricas"""
    logger.info("📊 Sistema de métricas inicializado")
    
    # Solo en producción por defecto
    if ENVIRONMENT == "production":
        logger.info("📈 Métricas habilitadas para producción")
    else:
        logger.info("📊 Métricas disponibles en /metrics (desarrollo)")
