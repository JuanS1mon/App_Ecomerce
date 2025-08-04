# ============================================================================
# GENERATOR_LOGGER.PY - SISTEMA DE LOGGING UNIFICADO
# ============================================================================
"""
Sistema de logging unificado para el generador de código.
Proporciona logging consistente, trazabilidad y manejo de errores.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

class GeneratorLogger:
    """Logger especializado para el generador de código"""
    
    def __init__(self, name: str = "generator", log_level: str = "INFO"):
        self.logger = logging.getLogger(f"generator.{name}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Configurar formato de logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # Handler para archivo
            log_file = Path("logs/generator.log")
            log_file.parent.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_generation_start(self, module_name: str, generator_type: str, options: Dict[str, Any] = None):
        """Log del inicio de generación"""
        options_str = json.dumps(options, ensure_ascii=False) if options else "Sin opciones"
        self.logger.info(f"🚀 INICIO - Generación {generator_type} para módulo '{module_name}' - Opciones: {options_str}")
    
    def log_generation_success(self, file_path: str, generator_type: str = "archivo"):
        """Log de generación exitosa"""
        self.logger.info(f"✅ ÉXITO - {generator_type.capitalize()} generado: {file_path}")
    
    def log_generation_error(self, error: Exception, context: str = "generación"):
        """Log de error en generación"""
        error_msg = str(error)
        trace = traceback.format_exc()
        self.logger.error(f"❌ ERROR - {context}: {error_msg}")
        self.logger.debug(f"💥 TRACEBACK - {context}:\n{trace}")
    
    def log_validation_error(self, error: Exception, field: str = "unknown"):
        """Log de error de validación"""
        self.logger.warning(f"⚠️ VALIDACIÓN - Error en {field}: {str(error)}")
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True):
        """Log de operaciones de archivo"""
        status_icon = "✅" if success else "❌"
        status_text = "ÉXITO" if success else "ERROR"
        self.logger.info(f"{status_icon} ARCHIVO - {operation} {file_path}: {status_text}")
    
    def log_directory_creation(self, directory: str, success: bool = True):
        """Log de creación de directorios"""
        status_icon = "📁" if success else "❌"
        status_text = "creado" if success else "error"
        self.logger.info(f"{status_icon} DIRECTORIO - {directory} {status_text}")
    
    def log_service_registration(self, service_id: str, success: bool = True):
        """Log de registro de servicios"""
        status_icon = "🔧" if success else "❌"
        status_text = "registrado" if success else "error en registro"
        self.logger.info(f"{status_icon} SERVICIO - {service_id} {status_text}")
    
    def log_template_render(self, template_name: str, success: bool = True):
        """Log de renderizado de templates"""
        status_icon = "📄" if success else "❌"
        status_text = "renderizado" if success else "error en renderizado"
        self.logger.info(f"{status_icon} TEMPLATE - {template_name} {status_text}")
    
    def log_user_action(self, action: str, user_data: Dict[str, Any] = None):
        """Log de acciones del usuario"""
        user_info = ""
        if user_data and user_data.get('user'):
            username = user_data['user'].get('username', 'unknown')
            user_info = f" - Usuario: {username}"
        self.logger.info(f"👤 USUARIO - {action}{user_info}")
    
    def log_performance(self, operation: str, duration: float, details: str = ""):
        """Log de rendimiento"""
        self.logger.info(f"⏱️ PERFORMANCE - {operation}: {duration:.3f}s {details}")
    
    def log_configuration(self, config_name: str, value: Any):
        """Log de configuración"""
        self.logger.debug(f"⚙️ CONFIG - {config_name}: {value}")
    
    def log_debug_info(self, message: str, data: Any = None):
        """Log de información de debug"""
        if data:
            data_str = json.dumps(data, ensure_ascii=False, default=str)
            self.logger.debug(f"🔍 DEBUG - {message}: {data_str}")
        else:
            self.logger.debug(f"🔍 DEBUG - {message}")

class GenerationSession:
    """Contexto de sesión para una operación de generación completa"""
    
    def __init__(self, module_name: str, generator_type: str, logger: GeneratorLogger):
        self.module_name = module_name
        self.generator_type = generator_type
        self.logger = logger
        self.start_time = datetime.now()
        self.generated_files = []
        self.errors = []
        self.warnings = []
    
    def __enter__(self):
        self.logger.log_generation_start(self.module_name, self.generator_type)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.log_generation_error(exc_val, f"sesión {self.generator_type}")
            self.logger.log_performance(f"Sesión {self.generator_type} (CON ERRORES)", duration)
        else:
            self.logger.log_performance(f"Sesión {self.generator_type} completada", duration, 
                                      f"- {len(self.generated_files)} archivos generados")
        
        # Log resumen de la sesión
        self.log_session_summary()
    
    def add_generated_file(self, file_path: str):
        """Agregar archivo generado a la sesión"""
        self.generated_files.append(file_path)
        self.logger.log_generation_success(file_path)
    
    def add_error(self, error: Exception, context: str = ""):
        """Agregar error a la sesión"""
        self.errors.append((error, context))
        self.logger.log_generation_error(error, context)
    
    def add_warning(self, message: str, context: str = ""):
        """Agregar advertencia a la sesión"""
        self.warnings.append((message, context))
        self.logger.logger.warning(f"⚠️ ADVERTENCIA - {context}: {message}")
    
    def log_session_summary(self):
        """Log del resumen de la sesión"""
        summary = {
            "módulo": self.module_name,
            "tipo": self.generator_type,
            "archivos_generados": len(self.generated_files),
            "errores": len(self.errors),
            "advertencias": len(self.warnings),
            "duración": (datetime.now() - self.start_time).total_seconds()
        }
        
        self.logger.logger.info(f"📊 RESUMEN SESIÓN - {json.dumps(summary, ensure_ascii=False)}")
        
        if self.generated_files:
            self.logger.logger.info(f"📁 ARCHIVOS GENERADOS:")
            for file_path in self.generated_files:
                self.logger.logger.info(f"   • {file_path}")

class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self, logger: GeneratorLogger):
        self.logger = logger
    
    def handle_validation_error(self, error: ValueError, field: str = "unknown") -> dict:
        """Manejar errores de validación"""
        self.logger.log_validation_error(error, field)
        return {
            "success": False,
            "error_type": "validation",
            "message": str(error),
            "field": field
        }
    
    def handle_file_error(self, error: Exception, file_path: str, operation: str = "operación") -> dict:
        """Manejar errores de archivo"""
        self.logger.log_generation_error(error, f"{operation} archivo {file_path}")
        return {
            "success": False,
            "error_type": "file",
            "message": f"Error en {operation} de {file_path}: {str(error)}",
            "file_path": file_path
        }
    
    def handle_generation_error(self, error: Exception, generator_type: str, module_name: str) -> dict:
        """Manejar errores de generación"""
        self.logger.log_generation_error(error, f"generación {generator_type} para {module_name}")
        return {
            "success": False,
            "error_type": "generation",
            "message": f"Error generando {generator_type} para {module_name}: {str(error)}",
            "generator_type": generator_type,
            "module_name": module_name
        }
    
    def handle_service_error(self, error: Exception, service_id: str, operation: str = "operación") -> dict:
        """Manejar errores de servicio"""
        self.logger.log_generation_error(error, f"{operation} servicio {service_id}")
        return {
            "success": False,
            "error_type": "service",
            "message": f"Error en {operation} del servicio {service_id}: {str(error)}",
            "service_id": service_id
        }

# Instancias globales para uso en toda la aplicación
main_logger = GeneratorLogger("main")
validator_logger = GeneratorLogger("validator")
service_logger = GeneratorLogger("service")
template_logger = GeneratorLogger("template")

# Manejador de errores global
error_handler = ErrorHandler(main_logger)
