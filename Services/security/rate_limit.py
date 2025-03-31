import time
from collections import defaultdict
import logging
from typing import Dict, Tuple
from fastapi import HTTPException, status, Request
import math

# Configuración de logging
logger = logging.getLogger("rate_limit")

# Estructura para almacenar información de intentos
# {ip_address: [(timestamp1, count1), (timestamp2, count2), ...]}
attempt_records: Dict[str, list] = defaultdict(list)

# Configuración
MAX_ATTEMPTS = 5  # Número máximo de intentos
TIME_WINDOW = 60  # Ventana de tiempo en segundos (1 minuto)
BLOCK_DURATION = 300  # Duración del bloqueo en segundos (5 minutos)

def check_rate_limit(request: Request, username: str = None):
    """
    Verifica si el cliente ha excedido el límite de intentos.
    Lanza una excepción HTTPException si se excede el límite.
    """
    # Obtener la dirección IP del cliente
    client_ip = request.client.host if request.client else "unknown"
    
    # Si se proporciona un nombre de usuario, usar combinación IP+usuario
    identifier = f"{client_ip}:{username}" if username else client_ip
    
    current_time = time.time()
    
    # Limpiar registros antiguos
    cleanup_old_records(identifier, current_time)
    
    # Contar intentos recientes
    recent_attempts = count_recent_attempts(identifier, current_time)
    
    # Verificar si está bloqueado
    if is_blocked(identifier, current_time):
        remaining_block_time = get_remaining_block_time(identifier, current_time)
        logger.warning(f"Acceso bloqueado para {identifier}. Tiempo restante: {remaining_block_time} segundos")
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos. Intente nuevamente en {math.ceil(remaining_block_time)} segundos",
        )
    
    # Registrar este intento
    record_attempt(identifier, current_time)
    
    # Si excede el número máximo de intentos, bloquear
    if recent_attempts >= MAX_ATTEMPTS:
        logger.warning(f"Límite de intentos excedido para {identifier}. Bloqueando por {BLOCK_DURATION} segundos")
        
        # Marcar como bloqueado
        mark_as_blocked(identifier, current_time)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos. Intente nuevamente en {BLOCK_DURATION} segundos",
        )

def cleanup_old_records(identifier: str, current_time: float):
    """Elimina registros antiguos fuera de la ventana de tiempo."""
    if identifier in attempt_records:
        attempt_records[identifier] = [
            (timestamp, count) for timestamp, count in attempt_records[identifier]
            if current_time - timestamp < TIME_WINDOW + BLOCK_DURATION
        ]

def count_recent_attempts(identifier: str, current_time: float) -> int:
    """Cuenta los intentos recientes dentro de la ventana de tiempo."""
    return sum(
        count for timestamp, count in attempt_records[identifier]
        if current_time - timestamp < TIME_WINDOW and count > 0
    )

def is_blocked(identifier: str, current_time: float) -> bool:
    """Verifica si el identificador está bloqueado."""
    for timestamp, count in attempt_records[identifier]:
        if count < 0:  # Un count negativo indica bloqueo
            block_time = timestamp
            if current_time - block_time < BLOCK_DURATION:
                return True
    return False

def get_remaining_block_time(identifier: str, current_time: float) -> float:
    """Obtiene el tiempo restante de bloqueo en segundos."""
    for timestamp, count in attempt_records[identifier]:
        if count < 0:  # Un count negativo indica bloqueo
            block_time = timestamp
            remaining = BLOCK_DURATION - (current_time - block_time)
            return max(0, remaining)
    return 0

def record_attempt(identifier: str, current_time: float):
    """Registra un intento."""
    attempt_records[identifier].append((current_time, 1))

def mark_as_blocked(identifier: str, current_time: float):
    """Marca un identificador como bloqueado."""
    attempt_records[identifier].append((current_time, -1))  # -1 indica bloqueo