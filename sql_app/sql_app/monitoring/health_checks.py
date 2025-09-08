# =============================
# HEALTH CHECKS AVANZADOS
# =============================
# Sistema de health checks multi-nivel para monitoreo completo

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import psutil
import os

# Importaciones de la aplicación
from sql_app.db.database import engine, get_db
from sql_app.cache.redis_cache import cache_manager
from sql_app.monitoring.notifications import notification_manager
from sql_app.config import ENVIRONMENT

logger = logging.getLogger("health_checks")

class HealthStatus(Enum):
    """Estados de salud del sistema"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Resultado de un health check"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    duration_ms: float
    timestamp: datetime

class AdvancedHealthChecker:
    """Sistema avanzado de health checks"""
    
    def __init__(self):
        self.checks = {}
        self.last_results = {}
        self.alert_cooldown = {}  # Para evitar spam de alertas
        self.cooldown_duration = 300  # 5 minutos
        
    async def register_check(self, name: str, check_func, interval: int = 60):
        """Registra un health check"""
        self.checks[name] = {
            'function': check_func,
            'interval': interval,
            'last_run': 0
        }
        logger.info(f"✅ Health check registrado: {name}")
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Ejecuta todos los health checks"""
        results = {}
        
        for name, check_config in self.checks.items():
            try:
                # Verificar si es tiempo de ejecutar
                now = time.time()
                if now - check_config['last_run'] < check_config['interval']:
                    # Usar resultado anterior si no es tiempo de ejecutar
                    if name in self.last_results:
                        results[name] = self.last_results[name]
                        continue
                
                # Ejecutar check
                start_time = time.time()
                result = await check_config['function']()
                duration = (time.time() - start_time) * 1000
                
                # Crear resultado
                health_check = HealthCheck(
                    name=name,
                    status=result['status'],
                    message=result['message'],
                    details=result.get('details', {}),
                    duration_ms=duration,
                    timestamp=datetime.now()
                )
                
                results[name] = health_check
                self.last_results[name] = health_check
                check_config['last_run'] = now
                
                # Enviar alerta si hay problemas
                await self._check_for_alerts(health_check)
                
            except Exception as e:
                logger.error(f"❌ Error en health check {name}: {e}")
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.CRITICAL,
                    message=f"Error ejecutando check: {str(e)}",
                    details={'error': str(e)},
                    duration_ms=0,
                    timestamp=datetime.now()
                )
        
        return results
    
    async def _check_for_alerts(self, health_check: HealthCheck):
        """Verifica si debe enviar alertas"""
        if health_check.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            # Verificar cooldown
            cooldown_key = f"{health_check.name}_{health_check.status.value}"
            now = time.time()
            
            if cooldown_key in self.alert_cooldown:
                if now - self.alert_cooldown[cooldown_key] < self.cooldown_duration:
                    return  # En cooldown, no enviar alerta
            
            # Enviar alerta
            severity = 'critical' if health_check.status == HealthStatus.CRITICAL else 'warning'
            await notification_manager.send_alert({
                'severity': severity,
                'summary': f"Health check failed: {health_check.name}",
                'description': health_check.message,
                'service': 'health-monitor'
            })
            
            # Establecer cooldown
            self.alert_cooldown[cooldown_key] = now
    
    def get_overall_status(self, results: Dict[str, HealthCheck]) -> HealthStatus:
        """Determina el estado general del sistema"""
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.WARNING

# =============================
# HEALTH CHECKS ESPECÍFICOS
# =============================

async def check_database() -> Dict[str, Any]:
    """Verifica el estado de la base de datos"""
    try:
        start_time = time.time()
        
        # Verificar conexión
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").fetchone()
            
        connection_time = (time.time() - start_time) * 1000
        
        # Verificar pool de conexiones
        pool_stats = {
            'size': engine.pool.size(),
            'checked_in': engine.pool.checkedin(),
            'checked_out': engine.pool.checkedout(),
            'overflow': engine.pool.overflow()
        }
        
        # Determinar estado
        if connection_time > 5000:  # > 5 segundos
            status = HealthStatus.CRITICAL
            message = f"Base de datos muy lenta: {connection_time:.0f}ms"
        elif connection_time > 1000:  # > 1 segundo
            status = HealthStatus.WARNING
            message = f"Base de datos lenta: {connection_time:.0f}ms"
        elif pool_stats['checked_out'] > 15:  # Muchas conexiones
            status = HealthStatus.WARNING
            message = f"Alto uso del pool: {pool_stats['checked_out']} conexiones"
        else:
            status = HealthStatus.HEALTHY
            message = f"Base de datos OK: {connection_time:.0f}ms"
        
        return {
            'status': status,
            'message': message,
            'details': {
                'connection_time_ms': connection_time,
                'pool_stats': pool_stats
            }
        }
        
    except Exception as e:
        return {
            'status': HealthStatus.CRITICAL,
            'message': f"Error de conexión a BD: {str(e)}",
            'details': {'error': str(e)}
        }

async def check_cache() -> Dict[str, Any]:
    """Verifica el estado del cache"""
    try:
        start_time = time.time()
        
        # Verificar cache
        test_key = "health_check_test"
        test_value = "test_value"
        
        # Operación de write/read
        cache_manager.set(test_key, test_value, ttl=60)
        retrieved = cache_manager.get(test_key)
        
        # Limpiar
        cache_manager.delete(test_key)
        
        operation_time = (time.time() - start_time) * 1000
        
        # Verificar resultado
        if retrieved != test_value:
            return {
                'status': HealthStatus.CRITICAL,
                'message': "Cache no funciona correctamente",
                'details': {'expected': test_value, 'got': retrieved}
            }
        
        # Verificar rendimiento
        if operation_time > 1000:  # > 1 segundo
            status = HealthStatus.WARNING
            message = f"Cache lento: {operation_time:.0f}ms"
        else:
            status = HealthStatus.HEALTHY
            message = f"Cache OK: {operation_time:.0f}ms"
        
        return {
            'status': status,
            'message': message,
            'details': {
                'operation_time_ms': operation_time,
                'backend': cache_manager.backend_type
            }
        }
        
    except Exception as e:
        return {
            'status': HealthStatus.WARNING,  # Warning, no crítico
            'message': f"Cache error (fallback activo): {str(e)}",
            'details': {'error': str(e)}
        }

async def check_system_resources() -> Dict[str, Any]:
    """Verifica recursos del sistema"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Determinar estado
        issues = []
        status = HealthStatus.HEALTHY
        
        if cpu_percent > 90:
            issues.append(f"CPU alta: {cpu_percent:.1f}%")
            status = HealthStatus.CRITICAL
        elif cpu_percent > 70:
            issues.append(f"CPU elevada: {cpu_percent:.1f}%")
            status = HealthStatus.WARNING
        
        if memory_percent > 90:
            issues.append(f"Memoria alta: {memory_percent:.1f}%")
            status = HealthStatus.CRITICAL
        elif memory_percent > 80:
            issues.append(f"Memoria elevada: {memory_percent:.1f}%")
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
        
        if disk_percent > 95:
            issues.append(f"Disco lleno: {disk_percent:.1f}%")
            status = HealthStatus.CRITICAL
        elif disk_percent > 85:
            issues.append(f"Poco espacio: {disk_percent:.1f}%")
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
        
        message = "; ".join(issues) if issues else "Recursos del sistema OK"
        
        return {
            'status': status,
            'message': message,
            'details': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk_percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        }
        
    except Exception as e:
        return {
            'status': HealthStatus.WARNING,
            'message': f"Error verificando recursos: {str(e)}",
            'details': {'error': str(e)}
        }

async def check_application_metrics() -> Dict[str, Any]:
    """Verifica métricas de la aplicación"""
    try:
        # Aquí podrías verificar métricas específicas
        # Por ejemplo, verificar que Prometheus esté recolectando métricas
        
        # Simulación de verificación de métricas
        from sql_app.monitoring.metrics import http_requests_total
        
        # Verificar que hay métricas
        samples = list(http_requests_total.collect())[0].samples
        
        if not samples:
            return {
                'status': HealthStatus.WARNING,
                'message': "No hay métricas HTTP disponibles",
                'details': {'samples_count': 0}
            }
        
        return {
            'status': HealthStatus.HEALTHY,
            'message': f"Métricas OK: {len(samples)} muestras",
            'details': {'samples_count': len(samples)}
        }
        
    except Exception as e:
        return {
            'status': HealthStatus.WARNING,
            'message': f"Error verificando métricas: {str(e)}",
            'details': {'error': str(e)}
        }

# =============================
# INSTANCIA GLOBAL
# =============================
health_checker = AdvancedHealthChecker()

async def init_health_checks():
    """Inicializa todos los health checks"""
    await health_checker.register_check("database", check_database, 60)
    await health_checker.register_check("cache", check_cache, 120)
    await health_checker.register_check("system_resources", check_system_resources, 180)
    await health_checker.register_check("application_metrics", check_application_metrics, 300)
    
    logger.info("🔍 Health checks inicializados")

async def get_health_status() -> Dict[str, Any]:
    """Obtiene el estado completo de salud del sistema"""
    results = await health_checker.run_all_checks()
    overall_status = health_checker.get_overall_status(results)
    
    return {
        'status': overall_status.value,
        'timestamp': datetime.now().isoformat(),
        'environment': ENVIRONMENT,
        'checks': {
            name: {
                'status': check.status.value,
                'message': check.message,
                'details': check.details,
                'duration_ms': check.duration_ms,
                'timestamp': check.timestamp.isoformat()
            }
            for name, check in results.items()
        }
    }
