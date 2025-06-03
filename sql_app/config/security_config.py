# config/security_config.py
"""
Configuración centralizada de seguridad para la aplicación FastAPI.
Este archivo contiene todas las configuraciones relacionadas con seguridad.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SecurityConfig:
    """Configuración de seguridad de la aplicación"""
    
    # Configuración JWT
    SECRET_KEY: str = os.getenv("SECRET", "default-secret-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_DURATION", "30"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_DURATION", "10080"))
    
    # Configuración JWT mejorada
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "fastapi-app")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "app-users")
    
    # Configuración de Rate Limiting
    RATE_LIMIT_MAX_ATTEMPTS: int = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "5"))
    RATE_LIMIT_TIME_WINDOW: int = int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60"))
    RATE_LIMIT_BLOCK_DURATION: int = int(os.getenv("RATE_LIMIT_BLOCK_DURATION", "300"))
    RATE_LIMIT_PROGRESSIVE_DELAY: bool = os.getenv("RATE_LIMIT_PROGRESSIVE_DELAY", "true").lower() == "true"
    RATE_LIMIT_MAX_DELAY: int = int(os.getenv("RATE_LIMIT_MAX_DELAY", "60"))
    
    # Configuración de Detección de Amenazas
    THREAT_DETECTION_ENABLED: bool = os.getenv("THREAT_DETECTION_ENABLED", "true").lower() == "true"
    BRUTE_FORCE_THRESHOLD: int = int(os.getenv("BRUTE_FORCE_THRESHOLD", "10"))
    BRUTE_FORCE_TIME_WINDOW: int = int(os.getenv("BRUTE_FORCE_TIME_WINDOW", "3600"))
    DDOS_PROTECTION_ENABLED: bool = os.getenv("DDoS_PROTECTION_ENABLED", "true").lower() == "true"
    DDOS_MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("DDoS_MAX_REQUESTS_PER_MINUTE", "60"))
    
    # Configuración de Contraseñas
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_UPPERCASE: bool = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWERCASE: bool = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    PASSWORD_REQUIRE_NUMBERS: bool = os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL: bool = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    PASSWORD_HASH_ROUNDS: int = int(os.getenv("PASSWORD_HASH_ROUNDS", "12"))
    
    # Configuración de Cookies
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")
    COOKIE_HTTPONLY: bool = os.getenv("COOKIE_HTTPONLY", "true").lower() == "true"
    
    # Configuración de Logging
    SECURITY_LOG_LEVEL: str = os.getenv("SECURITY_LOG_LEVEL", "INFO")
    SECURITY_LOG_FILE: str = os.getenv("SECURITY_LOG_FILE", "logs/security.log")
    
    # Configuración de Redis (para tokens revocados)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # Listas de control de acceso
    ALLOWED_IPS: List[str] = [ip.strip() for ip in os.getenv("ALLOWED_IPS", "").split(",") if ip.strip()]
    BLOCKED_USER_AGENTS: List[str] = [ua.strip() for ua in os.getenv("BLOCKED_USER_AGENTS", "").split(",") if ua.strip()]
    
    # URL base de la aplicación
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida la configuración de seguridad"""
        errors = []
        
        # Validar SECRET_KEY
        if cls.SECRET_KEY == "default-secret-change-in-production":
            errors.append("⚠️  ADVERTENCIA: SECRET_KEY usando valor por defecto. Cambiar en producción.")
        
        if len(cls.SECRET_KEY) < 32:
            errors.append("⚠️  ADVERTENCIA: SECRET_KEY debería tener al menos 32 caracteres.")
        
        # Validar configuración de tokens
        if cls.ACCESS_TOKEN_EXPIRE_MINUTES > 120:
            errors.append("⚠️  ADVERTENCIA: ACCESS_TOKEN_EXPIRE_MINUTES muy alto (>2 horas).")
        
        # Validar configuración de rate limiting
        if cls.RATE_LIMIT_MAX_ATTEMPTS > 10:
            errors.append("⚠️  ADVERTENCIA: RATE_LIMIT_MAX_ATTEMPTS muy alto.")
        
        # Mostrar errores si los hay
        if errors:
            print("🔒 Validación de configuración de seguridad:")
            for error in errors:
                print(f"   {error}")
            return False
        
        print("✅ Configuración de seguridad validada correctamente.")
        return True

# Instancia global de configuración
security_config = SecurityConfig()

# Validar configuración al importar el módulo
if __name__ == "__main__":
    security_config.validate_config()
