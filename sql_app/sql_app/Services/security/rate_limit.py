"""
Sistema de rate limiting mejorado con detección de amenazas
Incluye protección contra brute force, DDoS y análisis de patrones
"""

import time
from collections import defaultdict, deque
import logging
from typing import Dict, Tuple, Optional
from fastapi import HTTPException, status, Request
import math
import hashlib
from datetime import datetime, timedelta
import threading
import ipaddress
from dataclasses import dataclass

# Configuración de logging
logger = logging.getLogger("rate_limit_security")

@dataclass
class AttemptRecord:
    """Registro de intento de acceso"""
    timestamp: float
    success: bool
    ip: str
    username: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None

@dataclass
class ThreatAnalysis:
    """Análisis de amenazas"""
    threat_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0-1
    indicators: list
    recommended_action: str

# Configuración mejorada
class SecurityConfig:
    # Rate Limiting básico
    MAX_ATTEMPTS = 5
    TIME_WINDOW = 300  # 5 minutos en segundos
    BLOCK_DURATION = 900  # 15 minutos en segundos
    
    # Rate limiting progresivo
    PROGRESSIVE_DELAYS = [1, 2, 4, 8, 16, 32, 60]  # Segundos
    
    # Detección de brute force
    BRUTE_FORCE_THRESHOLD = 10
    BRUTE_FORCE_TIME_WINDOW = 3600  # 1 hora
    BRUTE_FORCE_BLOCK_DURATION = 3600 * 6  # 6 horas
    
    # Detección DDoS
    DDOS_REQUESTS_PER_MINUTE = 60
    DDOS_UNIQUE_ENDPOINTS_THRESHOLD = 10
    DDOS_BLOCK_DURATION = 1800  # 30 minutos
    
    # Whitelist/Blacklist
    WHITELIST_IPS = [
        "127.0.0.1",
        "::1",
        "localhost"
    ]
    
    # Patrones sospechosos
    SUSPICIOUS_USER_AGENTS = [
        "sqlmap",
        "nikto",
        "nmap",
        "burp",
        "scanner",
        "bot",
        "curl",
        "wget"
    ]
    
    MAX_RECORDS_PER_IP = 1000  # Evitar memory leaks

# Almacenes de datos thread-safe
attempt_records: Dict[str, deque] = defaultdict(lambda: deque(maxlen=SecurityConfig.MAX_RECORDS_PER_IP))
blocked_ips: Dict[str, dict] = {}
suspicious_patterns: Dict[str, list] = defaultdict(list)
successful_logins: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

# Lock para thread safety
records_lock = threading.RLock()

def get_client_identifier(request: Request, username: str = None) -> str:
    """Genera identificador único del cliente"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Considerar proxies y load balancers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        client_ip = real_ip.strip()
    
    if username:
        return f"{client_ip}:{username}"
    return client_ip

def is_ip_whitelisted(ip: str) -> bool:
    """Verifica si la IP está en whitelist"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        for whitelist_ip in SecurityConfig.WHITELIST_IPS:
            try:
                if ip_obj == ipaddress.ip_address(whitelist_ip):
                    return True
                # Verificar si es una red
                if '/' in whitelist_ip:
                    network = ipaddress.ip_network(whitelist_ip, strict=False)
                    if ip_obj in network:
                        return True
            except:
                if ip == whitelist_ip:
                    return True
        return False
    except:
        return ip in SecurityConfig.WHITELIST_IPS

def analyze_user_agent(user_agent: str) -> ThreatAnalysis:
    """Analiza User-Agent para detectar herramientas de ataque"""
    if not user_agent:
        return ThreatAnalysis(
            threat_level="MEDIUM",
            confidence=0.7,
            indicators=["missing_user_agent"],
            recommended_action="monitor"
        )
    
    user_agent_lower = user_agent.lower()
    suspicious_indicators = []
    
    for suspicious_ua in SecurityConfig.SUSPICIOUS_USER_AGENTS:
        if suspicious_ua in user_agent_lower:
            suspicious_indicators.append(f"suspicious_user_agent_{suspicious_ua}")
    
    # Analizar patrones comunes de bots maliciosos
    bot_patterns = [
        r"python",
        r"java",
        r"go-http-client",
        r"masscan",
        r"zmap",
        r"nuclei"
    ]
    
    import re
    for pattern in bot_patterns:
        if re.search(pattern, user_agent_lower):
            suspicious_indicators.append(f"bot_pattern_{pattern}")
    
    if suspicious_indicators:
        return ThreatAnalysis(
            threat_level="HIGH" if len(suspicious_indicators) > 1 else "MEDIUM",
            confidence=0.8 if len(suspicious_indicators) > 1 else 0.6,
            indicators=suspicious_indicators,
            recommended_action="block" if len(suspicious_indicators) > 1 else "monitor"
        )
    
    return ThreatAnalysis(
        threat_level="LOW",
        confidence=0.9,
        indicators=[],
        recommended_action="allow"
    )

def detect_brute_force_attack(identifier: str, current_time: float) -> bool:
    """Detecta ataques de fuerza bruta"""
    with records_lock:
        records = attempt_records[identifier]
        
        # Contar intentos fallidos en la ventana de tiempo
        failed_attempts = sum(
            1 for record in records 
            if (current_time - record.timestamp < SecurityConfig.BRUTE_FORCE_TIME_WINDOW 
                and not record.success)
        )
        
        return failed_attempts >= SecurityConfig.BRUTE_FORCE_THRESHOLD

def detect_ddos_attack(client_ip: str, request: Request, current_time: float) -> bool:
    """Detecta ataques DDoS"""
    with records_lock:
        records = attempt_records[client_ip]
        
        # Contar requests en el último minuto
        recent_requests = sum(
            1 for record in records 
            if current_time - record.timestamp < 60
        )
        
        if recent_requests > SecurityConfig.DDOS_REQUESTS_PER_MINUTE:
            return True
        
        # Verificar diversidad de endpoints
        recent_endpoints = set(
            record.endpoint for record in records 
            if (current_time - record.timestamp < 60 
                and record.endpoint)
        )
        
        if len(recent_endpoints) > SecurityConfig.DDOS_UNIQUE_ENDPOINTS_THRESHOLD:
            return True
        
        return False

def calculate_progressive_delay(identifier: str, current_time: float) -> int:
    """Calcula delay progresivo basado en intentos fallidos"""
    with records_lock:
        records = attempt_records[identifier]
        
        recent_failures = sum(
            1 for record in records 
            if (current_time - record.timestamp < SecurityConfig.TIME_WINDOW 
                and not record.success)
        )
        
        if recent_failures == 0:
            return 0
        
        delay_index = min(recent_failures - 1, len(SecurityConfig.PROGRESSIVE_DELAYS) - 1)
        return SecurityConfig.PROGRESSIVE_DELAYS[delay_index]

def is_blocked(identifier: str, current_time: float) -> Tuple[bool, float, str]:
    """Verifica si está bloqueado y retorna tiempo restante y razón"""
    if identifier in blocked_ips:
        block_info = blocked_ips[identifier]
        block_time = block_info['timestamp']
        block_duration = block_info['duration']
        block_reason = block_info['reason']
        
        if current_time - block_time < block_duration:
            remaining_time = block_duration - (current_time - block_time)
            return True, remaining_time, block_reason
        else:
            # Bloqueo expirado, remover
            del blocked_ips[identifier]
    
    return False, 0, ""

def block_identifier(identifier: str, current_time: float, duration: int, reason: str):
    """Bloquea un identificador"""
    blocked_ips[identifier] = {
        'timestamp': current_time,
        'duration': duration,
        'reason': reason
    }
    
    logger.warning(f"Bloqueando {identifier} por {duration} segundos. Razón: {reason}")

def record_attempt(identifier: str, current_time: float, success: bool, 
                  ip: str, username: str = None, user_agent: str = None, 
                  endpoint: str = None):
    """Registra un intento de acceso"""
    with records_lock:
        record = AttemptRecord(
            timestamp=current_time,
            success=success,
            ip=ip,
            username=username,
            user_agent=user_agent,
            endpoint=endpoint
        )
        
        attempt_records[identifier].append(record)

def cleanup_old_records(current_time: float):
    """Limpia registros antiguos para evitar memory leaks"""
    cutoff_time = current_time - SecurityConfig.BRUTE_FORCE_TIME_WINDOW
    
    with records_lock:
        # Limpiar attempt_records
        for identifier in list(attempt_records.keys()):
            records = attempt_records[identifier]
            while records and records[0].timestamp < cutoff_time:
                records.popleft()
            
            # Remover identificadores sin registros
            if not records:
                del attempt_records[identifier]
        
        # Limpiar blocked_ips expirados
        for identifier in list(blocked_ips.keys()):
            block_info = blocked_ips[identifier]
            if current_time - block_info['timestamp'] > block_info['duration']:
                del blocked_ips[identifier]

def get_threat_assessment(request: Request, username: str = None) -> ThreatAnalysis:
    """Evalúa nivel de amenaza de la request"""
    user_agent = request.headers.get("User-Agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
    # Análisis del User-Agent
    ua_analysis = analyze_user_agent(user_agent)
    
    indicators = ua_analysis.indicators.copy()
    threat_level = ua_analysis.threat_level
    confidence = ua_analysis.confidence
    
    # Verificar si viene de Tor o proxies conocidos
    if is_tor_exit_node(client_ip):
        indicators.append("tor_exit_node")
        threat_level = "HIGH"
        confidence = max(confidence, 0.8)
    
    # Verificar patrones de timing de requests
    if detect_automated_behavior(client_ip):
        indicators.append("automated_behavior")
        if threat_level == "LOW":
            threat_level = "MEDIUM"
    
    return ThreatAnalysis(
        threat_level=threat_level,
        confidence=confidence,
        indicators=indicators,
        recommended_action=ua_analysis.recommended_action
    )

def is_tor_exit_node(ip: str) -> bool:
    """Verifica si la IP es un nodo de salida de Tor (implementación básica)"""
    # En producción, consultar listas actualizadas de nodos Tor
    known_tor_ranges = [
        "127.0.0.1",  # Placeholder - en producción usar listas reales
    ]
    return ip in known_tor_ranges

def detect_automated_behavior(client_ip: str) -> bool:
    """Detecta comportamiento automatizado basado en patrones de timing"""
    with records_lock:
        records = attempt_records.get(client_ip, deque())
        
        if len(records) < 5:
            return False
        
        # Verificar intervalos regulares (indicativo de bots)
        recent_records = [r for r in records if time.time() - r.timestamp < 300]
        if len(recent_records) < 5:
            return False
        
        intervals = []
        for i in range(1, len(recent_records)):
            interval = recent_records[i].timestamp - recent_records[i-1].timestamp
            intervals.append(interval)
        
        # Si los intervalos son muy regulares, probablemente es un bot
        if len(intervals) > 3:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            
            # Varianza baja indica timing regular (bot)
            if variance < 1.0 and avg_interval < 10:
                return True
        
        return False

def check_rate_limit(request: Request, username: str = None):
    """Verificación principal de rate limiting con análisis de amenazas"""
    current_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    identifier = get_client_identifier(request, username)
    
    # Cleanup periódico
    if time.time() % 60 < 1:  # Cada minuto aproximadamente
        cleanup_old_records(current_time)
    
    # Verificar whitelist
    if is_ip_whitelisted(client_ip):
        return
    
    # Obtener información de la request
    user_agent = request.headers.get("User-Agent", "")
    endpoint = str(request.url.path)
    
    # Análisis de amenazas
    threat_analysis = get_threat_assessment(request, username)
    
    # Acción basada en análisis de amenazas
    if threat_analysis.recommended_action == "block":
        logger.warning(f"Bloqueando por análisis de amenazas: {identifier} - {threat_analysis.indicators}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado por actividad sospechosa"
        )
    
    # Verificar si está bloqueado
    is_blocked_flag, remaining_time, block_reason = is_blocked(identifier, current_time)
    if is_blocked_flag:
        logger.warning(f"Acceso bloqueado para {identifier}. Tiempo restante: {remaining_time:.0f}s. Razón: {block_reason}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Acceso bloqueado. Intente en {math.ceil(remaining_time)} segundos. Razón: {block_reason}",
            headers={"Retry-After": str(math.ceil(remaining_time))}
        )
    
    # Detectar ataques DDoS
    if detect_ddos_attack(client_ip, request, current_time):
        block_identifier(
            client_ip, 
            current_time, 
            SecurityConfig.DDOS_BLOCK_DURATION, 
            "DDoS attack detected"
        )
        logger.critical(f"DDoS attack detectado desde {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes detectadas",
            headers={"Retry-After": str(SecurityConfig.DDOS_BLOCK_DURATION)}
        )
    
    # Detectar brute force
    if detect_brute_force_attack(identifier, current_time):
        block_identifier(
            identifier, 
            current_time, 
            SecurityConfig.BRUTE_FORCE_BLOCK_DURATION, 
            "Brute force attack detected"
        )
        logger.critical(f"Brute force attack detectado para {identifier}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de inicio de sesión",
            headers={"Retry-After": str(SecurityConfig.BRUTE_FORCE_BLOCK_DURATION)}
        )
    
    # Calcular delay progresivo
    delay = calculate_progressive_delay(identifier, current_time)
    if delay > 0:
        logger.info(f"Aplicando delay progresivo de {delay}s para {identifier}")
        time.sleep(delay)
    
    # Registrar este intento
    record_attempt(
        identifier, 
        current_time, 
        False,  # Se marcará como True en record_successful_login
        client_ip, 
        username, 
        user_agent, 
        endpoint
    )

def record_successful_login(client_ip: str, username: str):
    """Registra login exitoso"""
    current_time = time.time()
    identifier = f"{client_ip}:{username}"
    
    with records_lock:
        # Marcar el último intento como exitoso
        records = attempt_records[identifier]
        if records and not records[-1].success:
            records[-1].success = True
        
        # Registrar en successful_logins
        successful_logins[identifier].append(current_time)
    
    logger.info(f"Login exitoso registrado para {username} desde {client_ip}")

def clear_attempts(request: Request, username: str):
    """Limpia intentos después de login exitoso"""
    identifier = get_client_identifier(request, username)
    
    with records_lock:
        if identifier in attempt_records:
            # Mantener solo los registros exitosos recientes
            current_time = time.time()
            successful_records = [
                record for record in attempt_records[identifier]
                if record.success and (current_time - record.timestamp < 3600)
            ]
            attempt_records[identifier].clear()
            attempt_records[identifier].extend(successful_records)
    
    logger.info(f"Intentos limpiados para {identifier}")

def get_security_stats() -> dict:
    """Obtiene estadísticas de seguridad"""
    current_time = time.time()
    
    with records_lock:
        total_attempts = sum(len(records) for records in attempt_records.values())
        blocked_count = len(blocked_ips)
        
        # Contar intentos fallidos recientes
        recent_failures = 0
        for records in attempt_records.values():
            recent_failures += sum(
                1 for record in records
                if (current_time - record.timestamp < 3600 and not record.success)
            )
        
        return {
            "total_attempts": total_attempts,
            "blocked_ips": blocked_count,
            "recent_failures": recent_failures,
            "successful_logins_last_hour": len([
                login_time for logins in successful_logins.values()
                for login_time in logins
                if current_time - login_time < 3600
            ])
        }
