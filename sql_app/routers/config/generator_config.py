# ============================================================================
# GENERATOR_CONFIG.PY - CONFIGURACIÓN CENTRALIZADA DEL GENERADOR
# ============================================================================
"""
Sistema de configuración centralizada para el generador de código.
Proporciona configuración unificada, validaciones y mapeos de tipos.
"""

from typing import Dict, List, Set
from dataclasses import dataclass, field
from pathlib import Path
import os

@dataclass
class GeneratorPaths:
    """Configuración de rutas para diferentes tipos de archivos generados"""
    models: str = "db/models"
    schemas: str = "db/schemas/Maestro"
    cruds: str = "db/crud/Maestro"
    routes: str = "routers/Maestros"
    services: str = "Services"
    html: str = "sql_app/static/html"
    tests: str = "tests"
    templates: str = "sql_app/static"

@dataclass
class GeneratorConfig:
    """Configuración principal del generador"""
    
    # Rutas de archivos
    paths: GeneratorPaths = field(default_factory=GeneratorPaths)
    
    # Tipos de campo permitidos
    allowed_field_types: Set[str] = field(default_factory=set)
    
    # Mapeo de tipos de campo a tipos Python
    field_type_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Mapeo de tipos de campo a tipos SQLAlchemy
    sqlalchemy_type_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Extensiones de archivo
    file_extensions: Dict[str, str] = field(default_factory=dict)
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Inicializar configuraciones por defecto"""
        if not self.allowed_field_types:
            self.allowed_field_types = {
                'string', 'str', 'text',
                'integer', 'int', 'number',
                'float', 'decimal', 'double',
                'boolean', 'bool',
                'datetime', 'date', 'time',
                'json', 'dict',
                'uuid', 'id'
            }
        
        if not self.field_type_mappings:
            self.field_type_mappings = {
                'string': 'str',
                'str': 'str', 
                'text': 'str',
                'integer': 'int',
                'int': 'int',
                'number': 'int',
                'float': 'float',
                'decimal': 'float',
                'double': 'float',
                'boolean': 'bool',
                'bool': 'bool',
                'datetime': 'datetime',
                'date': 'date',
                'time': 'time',
                'json': 'dict',
                'dict': 'dict',
                'uuid': 'str',
                'id': 'int'
            }
        
        if not self.sqlalchemy_type_mappings:
            self.sqlalchemy_type_mappings = {
                'string': 'String(255)',
                'str': 'String(255)',
                'text': 'Text',
                'integer': 'Integer',
                'int': 'Integer',
                'number': 'Integer',
                'float': 'Float',
                'decimal': 'Numeric(10, 2)',
                'double': 'Float',
                'boolean': 'Boolean',
                'bool': 'Boolean',
                'datetime': 'DateTime',
                'date': 'Date',
                'time': 'Time',
                'json': 'JSON',
                'dict': 'JSON',
                'uuid': 'String(36)',
                'id': 'Integer'
            }
        
        if not self.file_extensions:
            self.file_extensions = {
                'python': '.py',
                'html': '.html',
                'javascript': '.js',
                'css': '.css',
                'json': '.json'
            }

class GeneratorValidator:
    """Validador para datos de entrada del generador"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
    
    def validate_module_name(self, module_name: str) -> bool:
        """Validar nombre del módulo"""
        if not module_name:
            raise ValueError("❌ El nombre del módulo no puede estar vacío")
        
        if not module_name.replace('_', '').isalnum():
            raise ValueError("❌ El nombre del módulo solo puede contener letras, números y guiones bajos")
        
        if module_name[0].isdigit():
            raise ValueError("❌ El nombre del módulo no puede empezar con un número")
        
        if len(module_name) > 50:
            raise ValueError("❌ El nombre del módulo no puede tener más de 50 caracteres")
        
        return True
    
    def validate_field_names(self, field_names: List[str]) -> bool:
        """Validar nombres de campos"""
        if not field_names:
            raise ValueError("❌ Debe especificar al menos un campo")
        
        if len(field_names) > 50:
            raise ValueError("❌ No se pueden definir más de 50 campos")
        
        seen_fields = set()
        for field in field_names:
            if not field:
                raise ValueError("❌ Los nombres de campo no pueden estar vacíos")
            
            if not field.replace('_', '').isalnum():
                raise ValueError(f"❌ El campo '{field}' contiene caracteres inválidos")
            
            if field[0].isdigit():
                raise ValueError(f"❌ El campo '{field}' no puede empezar con un número")
            
            if field in seen_fields:
                raise ValueError(f"❌ El campo '{field}' está duplicado")
            
            seen_fields.add(field)
        
        return True
    
    def validate_field_types(self, field_types: List[str]) -> bool:
        """Validar tipos de campos"""
        if not field_types:
            raise ValueError("❌ Debe especificar los tipos de campo")
        
        for field_type in field_types:
            if not field_type:
                raise ValueError("❌ Los tipos de campo no pueden estar vacíos")
            
            if field_type.lower() not in self.config.allowed_field_types:
                allowed_types = ', '.join(sorted(self.config.allowed_field_types))
                raise ValueError(f"❌ Tipo de campo '{field_type}' no permitido. Tipos válidos: {allowed_types}")
        
        return True
    
    def validate_field_consistency(self, field_names: List[str], field_types: List[str]) -> bool:
        """Validar consistencia entre campos y tipos"""
        if len(field_names) != len(field_types):
            raise ValueError(f"❌ Inconsistencia: {len(field_names)} campos vs {len(field_types)} tipos")
        
        return True
    
    def validate_generation_options(self, options: dict) -> bool:
        """Validar opciones de generación"""
        valid_options = {
            'generate_crud', 'generate_route', 'generate_schema', 
            'generate_html_form', 'generate_tests', 'agregar_rutas', 
            'generate_service'
        }
        
        # Verificar que al menos una opción esté seleccionada
        if not any(options.get(opt, False) for opt in valid_options):
            raise ValueError("❌ Debe seleccionar al menos una opción de generación")
        
        return True
    
    def validate_all(self, module_name: str, field_names: List[str], 
                    field_types: List[str], options: dict) -> bool:
        """Validar todos los datos de entrada"""
        try:
            self.validate_module_name(module_name)
            self.validate_field_names(field_names)
            self.validate_field_types(field_types)
            self.validate_field_consistency(field_names, field_types)
            self.validate_generation_options(options)
            return True
        except ValueError as e:
            raise e

class PathManager:
    """Gestor de rutas para el generador"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.base_path = Path.cwd()
    
    def ensure_directory_exists(self, path: str) -> bool:
        """Crear directorio si no existe"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise OSError(f"❌ Error al crear directorio {path}: {str(e)}")
    
    def get_file_path(self, generator_type: str, module_name: str, prefix: str = "") -> str:
        """Obtener ruta completa para un archivo generado"""
        paths_map = {
            'model': self.config.paths.models,
            'schema': self.config.paths.schemas,
            'crud': self.config.paths.cruds,
            'route': self.config.paths.routes,
            'service': self.config.paths.services,
            'html': self.config.paths.html,
            'test': self.config.paths.tests
        }
        
        base_path = paths_map.get(generator_type)
        if not base_path:
            raise ValueError(f"❌ Tipo de generador desconocido: {generator_type}")
        
        filename = f"{prefix}{module_name}.py"
        if generator_type == 'html':
            filename = f"{module_name}.html"
        
        return os.path.join(base_path, filename)
    
    def get_service_directory(self, module_name: str) -> str:
        """Obtener directorio para un servicio"""
        return os.path.join(self.config.paths.services, module_name)
    
    def file_exists(self, file_path: str) -> bool:
        """Verificar si un archivo existe"""
        return Path(file_path).exists()

# Instancia global de configuración
GENERATOR_CONFIG = GeneratorConfig()
VALIDATOR = GeneratorValidator(GENERATOR_CONFIG)
PATH_MANAGER = PathManager(GENERATOR_CONFIG)
