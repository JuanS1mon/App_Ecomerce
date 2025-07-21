# =============================
# REDIS CACHE CONFIGURATION
# =============================
# Configuración de Redis para caché y sesiones

import redis
import json
import logging
from typing import Optional, Any, Union
from datetime import timedelta
import os
from sql_app.config import ENVIRONMENT

logger = logging.getLogger("redis_cache")

# Configuración de Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Pool de conexiones Redis
redis_pool = None
redis_client = None

def init_redis():
    """Inicializa la conexión a Redis"""
    global redis_pool, redis_client
    
    try:
        redis_pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={}
        )
        
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # Test de conexión
        redis_client.ping()
        logger.info(f"✅ Redis conectado exitosamente en {REDIS_HOST}:{REDIS_PORT}")
        return True
        
    except redis.ConnectionError as e:
        logger.warning(f"⚠️ Redis no disponible: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inicializando Redis: {e}")
        return False

def get_redis() -> Optional[redis.Redis]:
    """Obtiene cliente Redis"""
    return redis_client

class CacheManager:
    """Gestor de caché con fallback sin Redis"""
    
    def __init__(self):
        self.redis_available = False
        self._memory_cache = {}  # Fallback en memoria
        
    def initialize(self):
        """Inicializa el sistema de caché"""
        self.redis_available = init_redis()
        if not self.redis_available:
            logger.info("🔄 Usando caché en memoria como fallback")
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Almacena valor en caché"""
        try:
            if self.redis_available and redis_client:
                # Serializar el valor
                serialized_value = json.dumps(value) if not isinstance(value, str) else value
                redis_client.setex(key, expire, serialized_value)
                return True
            else:
                # Fallback a memoria
                self._memory_cache[key] = {
                    'value': value,
                    'expire': expire
                }
                return True
        except Exception as e:
            logger.error(f"❌ Error guardando en caché {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché"""
        try:
            if self.redis_available and redis_client:
                value = redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            else:
                # Fallback a memoria
                cached = self._memory_cache.get(key)
                return cached['value'] if cached else None
        except Exception as e:
            logger.error(f"❌ Error obteniendo del caché {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Elimina valor del caché"""
        try:
            if self.redis_available and redis_client:
                redis_client.delete(key)
                return True
            else:
                self._memory_cache.pop(key, None)
                return True
        except Exception as e:
            logger.error(f"❌ Error eliminando del caché {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica si existe la clave"""
        try:
            if self.redis_available and redis_client:
                return redis_client.exists(key) > 0
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"❌ Error verificando existencia {key}: {e}")
            return False

# Instancia global del gestor de caché
cache_manager = CacheManager()

# Funciones de conveniencia
def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """Función de conveniencia para guardar en caché"""
    return cache_manager.set(key, value, expire)

def cache_get(key: str) -> Optional[Any]:
    """Función de conveniencia para obtener del caché"""
    return cache_manager.get(key)

def cache_delete(key: str) -> bool:
    """Función de conveniencia para eliminar del caché"""
    return cache_manager.delete(key)

def cache_exists(key: str) -> bool:
    """Función de conveniencia para verificar existencia"""
    return cache_manager.exists(key)

# Decorador para cachear funciones
def cached(expire: int = 3600, key_prefix: str = ""):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generar clave única
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Intentar obtener del caché
            cached_result = cache_get(cache_key)
            if cached_result is not None:
                logger.debug(f"📋 Cache hit para {func.__name__}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_set(cache_key, result, expire)
            logger.debug(f"💾 Cacheado resultado de {func.__name__}")
            return result
        return wrapper
    return decorator
