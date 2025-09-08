# =============================
# RATE LIMITING MIDDLEWARE
# =============================
# Middleware para control de tasa de peticiones

import time
import hashlib
from typing import Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
import logging
from sql_app.cache.redis_cache import cache_manager
from sql_app.config import ENVIRONMENT

logger = logging.getLogger("rate_limiter")

class RateLimitConfig:
    """Configuración de rate limiting por endpoint"""
    
    # Configuraciones por endpoint
    LIMITS = {
        # Endpoints críticos de autenticación
        "POST:/login": {"requests": 5, "window": 300},  # 5 req/5min
        "POST:/auth/token": {"requests": 5, "window": 300},
        "POST:/registro": {"requests": 3, "window": 600},  # 3 req/10min
        
        # API endpoints generales
        "GET:/api/": {"requests": 100, "window": 60},  # 100 req/min
        "POST:/api/": {"requests": 50, "window": 60},   # 50 req/min
        "PUT:/api/": {"requests": 30, "window": 60},    # 30 req/min
        "DELETE:/api/": {"requests": 20, "window": 60}, # 20 req/min
        
        # Endpoints de stock (críticos para el negocio)
        "GET:/stock/": {"requests": 200, "window": 60},  # 200 req/min
        "POST:/stock/": {"requests": 50, "window": 60},
        
        # Endpoints de admin (más restrictivos)
        "POST:/admin/": {"requests": 20, "window": 60},
        "DELETE:/admin/": {"requests": 10, "window": 60},
        
        # Default para endpoints no especificados
        "default": {"requests": 60, "window": 60}  # 60 req/min
    }
    
    # Rate limiting más laxo en desarrollo
    if ENVIRONMENT == "development":
        for endpoint in LIMITS:
            LIMITS[endpoint]["requests"] *= 10  # 10x más requests en desarrollo

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting con Redis/memoria"""
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = ENVIRONMENT == "production"  # Solo en producción por defecto
        
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
            
        # Obtener información de la petición
        client_ip = self._get_client_ip(request)
        method = request.method
        path = self._normalize_path(request.url.path)
        endpoint_key = f"{method}:{path}"
        
        # Obtener configuración de rate limit
        limit_config = self._get_limit_config(endpoint_key)
        
        # Verificar rate limit
        is_allowed, remaining, reset_time = await self._check_rate_limit(
            client_ip, endpoint_key, limit_config
        )
        
        if not is_allowed:
            logger.warning(f"🚫 Rate limit excedido para {client_ip} en {endpoint_key}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Demasiadas peticiones. Límite: {limit_config['requests']} por {limit_config['window']} segundos",
                    "retry_after": reset_time
                },
                headers={
                    "X-RateLimit-Limit": str(limit_config['requests']),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time)
                }
            )
        
        # Continuar con la petición
        response = await call_next(request)
        
        # Agregar headers informativos
        response.headers["X-RateLimit-Limit"] = str(limit_config['requests'])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP real del cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _normalize_path(self, path: str) -> str:
        """Normaliza el path para agrupar rutas similares"""
        # Remover IDs específicos para agrupar endpoints
        import re
        
        # Reemplazar números por placeholder
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Agrupar rutas API
        if path.startswith('/api/'):
            return '/api/'
        elif path.startswith('/stock/'):
            return '/stock/'
        elif path.startswith('/admin/'):
            return '/admin/'
        
        return path
    
    def _get_limit_config(self, endpoint_key: str) -> Dict[str, int]:
        """Obtiene configuración de límite para el endpoint"""
        config = RateLimitConfig.LIMITS.get(endpoint_key)
        if config:
            return config
        
        # Buscar por prefijo
        for pattern, conf in RateLimitConfig.LIMITS.items():
            if pattern != "default" and endpoint_key.endswith(pattern.split(':')[1]):
                return conf
        
        # Usar configuración por defecto
        return RateLimitConfig.LIMITS["default"]
    
    async def _check_rate_limit(self, client_ip: str, endpoint: str, config: Dict[str, int]) -> tuple:
        """Verifica si la petición está dentro del límite"""
        current_time = int(time.time())
        window = config['window']
        max_requests = config['requests']
        
        # Crear clave única para el cliente y endpoint
        key = f"rate_limit:{client_ip}:{endpoint}:{current_time // window}"
        
        try:
            # Obtener contador actual
            current_requests = cache_manager.get(key) or 0
            
            if isinstance(current_requests, str):
                current_requests = int(current_requests)
            
            if current_requests >= max_requests:
                reset_time = ((current_time // window) + 1) * window - current_time
                return False, 0, reset_time
            
            # Incrementar contador
            new_count = current_requests + 1
            cache_manager.set(key, new_count, window)
            
            remaining = max_requests - new_count
            reset_time = ((current_time // window) + 1) * window - current_time
            
            return True, remaining, reset_time
            
        except Exception as e:
            logger.error(f"❌ Error en rate limiting: {e}")
            # En caso de error, permitir la petición
            return True, max_requests, window

# Función para habilitar/deshabilitar rate limiting dinámicamente
def enable_rate_limiting(enabled: bool = True):
    """Habilita o deshabilita el rate limiting"""
    RateLimitMiddleware.enabled = enabled
    logger.info(f"🔧 Rate limiting {'habilitado' if enabled else 'deshabilitado'}")

# Función para ajustar límites dinámicamente
def update_rate_limits(endpoint: str, requests: int, window: int):
    """Actualiza límites de rate limiting para un endpoint"""
    RateLimitConfig.LIMITS[endpoint] = {"requests": requests, "window": window}
    logger.info(f"🔧 Rate limit actualizado para {endpoint}: {requests} req/{window}s")
