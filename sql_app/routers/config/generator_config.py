# ============================================================================
# GENERATOR_CONFIG.PY - CONFIGURACIÓN CENTRALIZADA DEL GENERADOR
# ============================================================================
"""
Sistema de configuración centralizada para el generador de código.
Proporciona configuración unificada, validaciones y mapeos de tipos.
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os

# ============================================================================
# NUEVAS CLASES PARA SISTEMA MULTI-TABLA (FASE 1)
# ============================================================================

@dataclass
class RelationshipConfig:
    """Configuración avanzada para relaciones entre tablas (Fase 2)"""
    relationship_type: str  # "one_to_many", "many_to_one", "one_to_one", "many_to_many"
    from_table: str
    from_field: str
    to_table: str
    to_field: str
    relationship_name: str
    back_populates: Optional[str] = None
    cascade_delete: bool = False
    lazy_loading: str = "select"  # "select", "joined", "subquery", "dynamic"
    
    # NUEVAS FUNCIONALIDADES FASE 2
    # Many-to-Many específico
    junction_table: Optional[str] = None  # Tabla de unión para many-to-many
    junction_table_schema: Optional[Dict] = None  # Esquema de tabla de unión
    
    # Configuración avanzada
    order_by: Optional[str] = None  # Campo para ordenar relaciones
    filter_condition: Optional[str] = None  # Condición de filtro
    join_depth: int = 1  # Profundidad de JOIN (para queries complejas)
    
    # Índices y optimización
    create_index: bool = True  # Crear índices automáticamente
    index_name: Optional[str] = None  # Nombre personalizado del índice
    
    def __post_init__(self):
        """Validar configuración de relación avanzada"""
        # Normalizar tipo de relación: convertir guiones a guiones bajos
        if self.relationship_type:
            self.relationship_type = self.relationship_type.replace("-", "_")
        
        valid_types = ["one_to_many", "many_to_one", "one_to_one", "many_to_many"]
        if self.relationship_type not in valid_types:
            raise ValueError(f"Tipo de relación inválido: {self.relationship_type}. Tipos válidos: {valid_types}")
        
        # Para many-to-many, generar tabla de unión automáticamente si no se especifica
        if self.relationship_type == "many_to_many" and not self.junction_table:
            self.junction_table = f"{self.from_table}_{self.to_table}"
        
        if not self.back_populates:
            # Auto-generar back_populates si no se especifica
            self.back_populates = f"{self.from_table}_rel"
        
        # Auto-generar nombre de índice si se requiere
        if self.create_index and not self.index_name:
            self.index_name = f"idx_{self.from_table}_{self.to_table}"

@dataclass 
class FieldConfig:
    """Configuración avanzada para campos de tabla (Fase 2)"""
    name: str
    field_type: str
    max_length: Optional[int] = None
    nullable: bool = True
    unique: bool = False
    primary_key: bool = False
    auto_increment: bool = False
    default_value: Optional[str] = None
    foreign_key: Optional[str] = None  # Formato: "tabla.campo"
    index: bool = False
    
    # NUEVAS FUNCIONALIDADES FASE 2
    # Validaciones avanzadas
    min_value: Optional[float] = None  # Valor mínimo para números
    max_value: Optional[float] = None  # Valor máximo para números
    regex_pattern: Optional[str] = None  # Patrón de validación
    enum_values: Optional[List[str]] = None  # Valores enum permitidos
    
    # Metadatos y documentación
    description: Optional[str] = None  # Descripción del campo
    example_value: Optional[str] = None  # Valor de ejemplo
    is_sensitive: bool = False  # Campo sensible (PII)
    
    # Configuración de base de datos
    collation: Optional[str] = None  # Collation para strings
    precision: Optional[int] = None  # Precisión para decimales
    scale: Optional[int] = None  # Escala para decimales
    
    # Funcionalidades especiales
    is_searchable: bool = True  # Si aparece en búsquedas
    is_sortable: bool = True  # Si permite ordenamiento
    is_filterable: bool = True  # Si permite filtros
    
    def get_sqlalchemy_type(self) -> str:
        """Convierte el tipo de campo a tipo SQLAlchemy (mejorado para Fase 2)"""
        type_mapping = {
            'string': f'String({self.max_length or 255})',
            'integer': 'Integer',
            'bigint': 'BigInteger',
            'smallint': 'SmallInteger',
            'float': 'Float',
            'decimal': f'Numeric({self.precision or 10}, {self.scale or 2})',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'text': 'Text',
            'longtext': 'Text',
            'json': 'JSON',
            'uuid': 'String(36)',  # Para UUIDs
            'email': 'String(255)',  # Email específico
            'url': 'String(2048)',  # URLs
            'phone': 'String(20)',  # Teléfonos
            'enum': 'Enum' if self.enum_values else 'String(50)'
        }
        return type_mapping.get(self.field_type, 'String(255)')
    
    def get_column_definition(self) -> str:
        """Genera la definición completa de la columna (mejorada)"""
        parts = [self.get_sqlalchemy_type()]
        
        if self.foreign_key:
            parts.append(f'ForeignKey("{self.foreign_key}")')
        if self.primary_key:
            parts.append('primary_key=True')
        if self.auto_increment and self.primary_key:
            parts.append('autoincrement=True')
        if not self.nullable:
            parts.append('nullable=False')
        if self.unique:
            parts.append('unique=True')
        if self.index:
            parts.append('index=True')
        if self.default_value:
            if self.field_type in ['string', 'text']:
                parts.append(f'default="{self.default_value}"')
            else:
                parts.append(f'default={self.default_value}')
                
        return f'Column({", ".join(parts)})'

@dataclass
class TableConfig:
    """Configuración avanzada para una tabla individual (Fase 2)"""
    name: str
    fields: List[FieldConfig]
    relationships: List[RelationshipConfig] = field(default_factory=list)
    description: Optional[str] = None
    
    # NUEVAS FUNCIONALIDADES FASE 2
    # Configuración de tabla
    table_engine: str = "InnoDB"  # Motor de tabla (MySQL)
    table_charset: str = "utf8mb4"  # Charset
    table_collation: str = "utf8mb4_unicode_ci"  # Collation
    
    # Metadatos y organización
    category: Optional[str] = None  # Categoría de la tabla
    tags: List[str] = field(default_factory=list)  # Etiquetas
    priority: int = 1  # Prioridad para ordenamiento
    
    # Configuración de acceso
    is_public: bool = True  # Acceso público
    requires_auth: bool = False  # Requiere autenticación
    permissions: List[str] = field(default_factory=list)  # Permisos específicos
    
    # Optimización y rendimiento
    enable_soft_delete: bool = False  # Borrado lógico
    enable_versioning: bool = False  # Versionado de registros
    enable_audit_trail: bool = False  # Auditoría de cambios
    cache_ttl: Optional[int] = None  # TTL para cache (segundos)
    
    # Configuración de interfaz
    display_field: Optional[str] = None  # Campo principal para mostrar
    search_fields: List[str] = field(default_factory=list)  # Campos de búsqueda
    default_order: Optional[str] = None  # Ordenamiento por defecto
    
    def get_model_name(self) -> str:
        """Obtiene el nombre de la clase del modelo"""
        return self.name.title().replace('_', '')
    
    def get_primary_key_field(self) -> Optional[FieldConfig]:
        """Obtiene el campo que es primary key"""
        for field_config in self.fields:
            if field_config.primary_key:
                return field_config
        return None
    
    def get_foreign_key_fields(self) -> List[FieldConfig]:
        """Obtiene todos los campos que son foreign keys"""
        return [field for field in self.fields if field.foreign_key]
    
    def get_searchable_fields(self) -> List[FieldConfig]:
        """Obtiene campos configurados como buscables"""
        if self.search_fields:
            return [field for field in self.fields if field.name in self.search_fields]
        return [field for field in self.fields if field.is_searchable]

@dataclass
class MultiTableServiceConfig:
    """Configuración avanzada para un servicio multi-tabla (Fase 2)"""
    service_name: str
    description: str
    tables: List[TableConfig]
    relationships: List[RelationshipConfig] = field(default_factory=list)
    generate_crud_for_all: bool = True
    generate_relationship_endpoints: bool = True
    
    # NUEVAS FUNCIONALIDADES FASE 2
    # Configuración del servicio
    version: str = "1.0.0"  # Versión del servicio
    author: Optional[str] = None  # Autor del servicio
    license: str = "MIT"  # Licencia
    
    # Configuración avanzada de generación
    generate_many_to_many: bool = True  # Generar tablas many-to-many
    generate_junction_tables: bool = True  # Generar tablas de unión
    generate_complex_queries: bool = True  # Queries con múltiples JOINs
    generate_aggregation_endpoints: bool = True  # Endpoints de agregación
    
    # Configuración de API
    api_prefix: str = "/api/v1"  # Prefijo de la API
    enable_pagination: bool = True  # Paginación automática
    default_page_size: int = 20  # Tamaño de página por defecto
    max_page_size: int = 100  # Tamaño máximo de página
    
    # Configuración de seguridad
    enable_rate_limiting: bool = False  # Rate limiting
    enable_cors: bool = True  # CORS
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])  # Orígenes permitidos
    
    # Configuración de documentación
    generate_openapi_docs: bool = True  # Documentación OpenAPI
    include_examples: bool = True  # Incluir ejemplos
    generate_postman_collection: bool = False  # Colección Postman
    
    # Templates y patrones
    base_template: Optional[str] = None  # Template base a usar
    design_patterns: List[str] = field(default_factory=list)  # Patrones de diseño
    
    def get_main_table(self) -> Optional[TableConfig]:
        """Obtiene la tabla principal (primera en la lista)"""
        return self.tables[0] if self.tables else None
    
    def get_table_by_name(self, name: str) -> Optional[TableConfig]:
        """Obtiene una tabla por su nombre"""
        for table in self.tables:
            if table.name == name:
                return table
        return None
    
    def validate_relationships(self) -> List[str]:
        """Valida que todas las relaciones referencien tablas existentes"""
        errors = []
        table_names = {table.name for table in self.tables}
        
        for rel in self.relationships:
            if rel.from_table not in table_names:
                errors.append(f"Tabla origen '{rel.from_table}' no existe en la configuración")
            if rel.to_table not in table_names:
                errors.append(f"Tabla destino '{rel.to_table}' no existe en la configuración")
                
        return errors
    
    def get_many_to_many_relationships(self) -> List[RelationshipConfig]:
        """Obtiene todas las relaciones many-to-many"""
        return [rel for rel in self.relationships if rel.relationship_type == "many_to_many"]
    
    def get_junction_tables_needed(self) -> List[str]:
        """Obtiene lista de tablas de unión necesarias"""
        junction_tables = []
        for rel in self.get_many_to_many_relationships():
            if rel.junction_table and rel.junction_table not in junction_tables:
                junction_tables.append(rel.junction_table)
        return junction_tables
    
    def estimate_complexity(self) -> Dict[str, int]:
        """Estima la complejidad del servicio"""
        return {
            "tables_count": len(self.tables),
            "fields_count": sum(len(table.fields) for table in self.tables),
            "relationships_count": len(self.relationships),
            "many_to_many_count": len(self.get_many_to_many_relationships()),
            "junction_tables_count": len(self.get_junction_tables_needed()),
            "complexity_score": len(self.tables) * 10 + len(self.relationships) * 5
        }

# ============================================================================
# CONFIGURACIÓN ORIGINAL (MANTENIDA PARA COMPATIBILIDAD)
# ============================================================================

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
                # Tipos básicos originales
                'string', 'str', 'text',
                'integer', 'int', 'number',
                'float', 'decimal', 'double',
                'boolean', 'bool',
                'datetime', 'date', 'time',
                'json', 'dict',
                'uuid', 'id',
                
                # NUEVOS TIPOS FASE 2
                'email',        # Email específico
                'url',          # URLs
                'phone',        # Números de teléfono
                'enum',         # Enums
                'bigint',       # Enteros grandes
                'smallint',     # Enteros pequeños
                'longtext',     # Texto largo
                'color',        # Códigos de color
                'currency',     # Valores monetarios
                'percentage'    # Porcentajes
            }
        
        if not self.field_type_mappings:
            self.field_type_mappings = {
                # Tipos básicos originales
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
                'id': 'int',
                
                # NUEVOS TIPOS FASE 2
                'email': 'str',
                'url': 'str',
                'phone': 'str',
                'enum': 'str',
                'bigint': 'int',
                'smallint': 'int',
                'longtext': 'str',
                'color': 'str',
                'currency': 'float',
                'percentage': 'float'
            }
        
        if not self.sqlalchemy_type_mappings:
            self.sqlalchemy_type_mappings = {
                # Tipos básicos originales
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
                'id': 'Integer',
                
                # NUEVOS TIPOS FASE 2
                'email': 'String(255)',
                'url': 'String(2048)',
                'phone': 'String(20)',
                'enum': 'String(50)',
                'bigint': 'BigInteger',
                'smallint': 'SmallInteger',
                'longtext': 'Text',
                'color': 'String(7)',
                'currency': 'Numeric(12, 2)',
                'percentage': 'Numeric(5, 2)'
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

# ============================================================================
# VALIDADOR MULTI-TABLA (FASE 1)
# ============================================================================

class MultiTableValidator:
    """Validador especializado para configuraciones multi-tabla"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.base_validator = GeneratorValidator(config)
    
    def validate_service_config(self, service_config: MultiTableServiceConfig) -> List[str]:
        """Validar configuración completa del servicio multi-tabla"""
        errors = []
        
        # Validar nombre del servicio
        try:
            self.base_validator.validate_module_name(service_config.service_name)
        except ValueError as e:
            errors.append(str(e))
        
        # Validar que hay al menos una tabla
        if not service_config.tables:
            errors.append("❌ Debe definir al menos una tabla")
        
        # Validar cada tabla
        for i, table in enumerate(service_config.tables):
            table_errors = self.validate_table_config(table, i + 1)
            errors.extend(table_errors)
        
        # Validar relaciones
        relationship_errors = service_config.validate_relationships()
        errors.extend(relationship_errors)
        
        # Validar consistencia de relaciones
        for rel in service_config.relationships:
            rel_errors = self.validate_relationship_config(rel, service_config)
            errors.extend(rel_errors)
        
        return errors
    
    def validate_table_config(self, table: TableConfig, table_number: int) -> List[str]:
        """Validar configuración de una tabla individual"""
        errors = []
        
        # Validar nombre de tabla
        try:
            self.base_validator.validate_module_name(table.name)
        except ValueError as e:
            errors.append(f"Tabla {table_number}: {str(e)}")
        
        # Validar que tiene campos
        if not table.fields:
            errors.append(f"❌ Tabla '{table.name}' debe tener al menos un campo")
        
        # Validar que tiene primary key
        has_pk = any(field.primary_key for field in table.fields)
        if not has_pk:
            errors.append(f"❌ Tabla '{table.name}' debe tener al menos un campo primary key")
        
        # Validar cada campo
        field_names = []
        for field in table.fields:
            field_errors = self.validate_field_config(field, table.name)
            errors.extend(field_errors)
            field_names.append(field.name)
        
        # Validar nombres de campo únicos
        if len(field_names) != len(set(field_names)):
            errors.append(f"❌ Tabla '{table.name}' tiene campos duplicados")
        
        return errors
    
    def validate_field_config(self, field: FieldConfig, table_name: str) -> List[str]:
        """Validar configuración de un campo"""
        errors = []
        
        # Validar nombre del campo
        try:
            self.base_validator.validate_field_names([field.name])
        except ValueError as e:
            errors.append(f"Campo '{field.name}' en tabla '{table_name}': {str(e)}")
        
        # Validar tipo del campo
        try:
            self.base_validator.validate_field_types([field.field_type])
        except ValueError as e:
            errors.append(f"Campo '{field.name}' en tabla '{table_name}': {str(e)}")
        
        # Validaciones específicas para foreign keys
        if field.foreign_key:
            if '.' not in field.foreign_key:
                errors.append(f"❌ Foreign key '{field.foreign_key}' debe tener formato 'tabla.campo'")
            
            if field.primary_key:
                errors.append(f"❌ Campo '{field.name}' no puede ser primary key y foreign key a la vez")
        
        # Validar auto_increment solo en primary keys enteros
        if field.auto_increment:
            if not field.primary_key:
                errors.append(f"❌ Campo '{field.name}' tiene auto_increment pero no es primary key")
            if field.field_type not in ['integer', 'int']:
                errors.append(f"❌ Campo '{field.name}' tiene auto_increment pero no es tipo integer")
        
        return errors
    
    def validate_relationship_config(self, relationship: RelationshipConfig, 
                                   service_config: MultiTableServiceConfig) -> List[str]:
        """Validar configuración de una relación"""
        errors = []
        
        from_table = service_config.get_table_by_name(relationship.from_table)
        to_table = service_config.get_table_by_name(relationship.to_table)
        
        if not from_table:
            errors.append(f"❌ Tabla origen '{relationship.from_table}' no encontrada")
            return errors
        
        if not to_table:
            errors.append(f"❌ Tabla destino '{relationship.to_table}' no encontrada")
            return errors
        
        # Validar que los campos existen
        from_field_exists = any(f.name == relationship.from_field for f in from_table.fields)
        to_field_exists = any(f.name == relationship.to_field for f in to_table.fields)
        
        if not from_field_exists:
            errors.append(f"❌ Campo '{relationship.from_field}' no existe en tabla '{relationship.from_table}'")
        
        if not to_field_exists:
            errors.append(f"❌ Campo '{relationship.to_field}' no existe en tabla '{relationship.to_table}'")
        
        return errors
    
    def validate_json_structure(self, json_data: dict) -> List[str]:
        """Validar estructura JSON para configuración multi-tabla"""
        errors = []
        required_fields = ['service_name', 'description', 'tables']
        
        for field in required_fields:
            if field not in json_data:
                errors.append(f"❌ Campo requerido '{field}' faltante en JSON")
        
        if 'tables' in json_data:
            if not isinstance(json_data['tables'], list):
                errors.append("❌ 'tables' debe ser una lista")
            elif len(json_data['tables']) < 1:
                errors.append("❌ Debe definir al menos una tabla")
        
        return errors

# Instancia global del validador multi-tabla
MULTI_TABLE_VALIDATOR = MultiTableValidator(GENERATOR_CONFIG)
