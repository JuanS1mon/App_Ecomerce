# ============================================================================
# GENERATOR_FACTORY.PY - FACTORY PATTERN Y CLASES BASE
# ============================================================================
"""
Sistema de Factory Pattern para generadores de código.
Proporciona una arquitectura extensible y mantenible.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from .generator_config import GENERATOR_CONFIG, VALIDATOR, PATH_MANAGER
from .generator_logger import GeneratorLogger, GenerationSession, error_handler

class BaseGenerator(ABC):
    """Clase base abstracta para todos los generadores"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.logger = GeneratorLogger(generator_type)
        self.config = GENERATOR_CONFIG
        self.path_manager = PATH_MANAGER
        self.validator = VALIDATOR
    
    @abstractmethod
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar el contenido del archivo"""
        pass
    
    @abstractmethod
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener la ruta del archivo a generar"""
        pass
    
    def validate_inputs(self, module_name: str, field_names: List[str], 
                       field_types: List[str], **kwargs) -> bool:
        """Validar entradas para este generador específico"""
        return self.validator.validate_all(
            module_name, field_names, field_types, 
            kwargs.get('options', {})
        )
    
    def prepare_data(self, module_name: str, field_names: List[str], 
                    field_types: List[str]) -> Dict[str, Any]:
        """Preparar datos para la generación"""
        return {
            'module_name': module_name.lower(),
            'module_name_cap': module_name.capitalize(),
            'field_names': [field.lower() for field in field_names],
            'field_types': [field_type.lower() for field_type in field_types],
            'field_mappings': [
                {
                    'name': field.lower(),
                    'type': field_type.lower(),
                    'python_type': self.config.field_type_mappings.get(field_type.lower(), 'str'),
                    'sqlalchemy_type': self.config.sqlalchemy_type_mappings.get(field_type.lower(), 'String(255)')
                }
                for field, field_type in zip(field_names, field_types)
            ]
        }
    
    def ensure_directory(self, file_path: str) -> bool:
        """Asegurar que existe el directorio del archivo"""
        try:
            directory = os.path.dirname(file_path)
            self.path_manager.ensure_directory_exists(directory)
            self.logger.log_directory_creation(directory, True)
            return True
        except Exception as e:
            self.logger.log_directory_creation(directory, False)
            raise e
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Guardar archivo con manejo de errores"""
        try:
            # Verificar si el archivo ya existe
            if self.path_manager.file_exists(file_path):
                self.logger.logger.warning(f"⚠️ ARCHIVO - {file_path} ya existe, será sobrescrito")
            
            # Asegurar que existe el directorio
            self.ensure_directory(file_path)
            
            # Escribir el archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.log_file_operation("guardado", file_path, True)
            return True
            
        except Exception as e:
            self.logger.log_file_operation("guardado", file_path, False)
            raise e
    
    def generate_and_save(self, module_name: str, field_names: List[str], 
                         field_types: List[str], **kwargs) -> Dict[str, Any]:
        """Método principal para generar y guardar"""
        try:
            # Validar entradas
            self.validate_inputs(module_name, field_names, field_types, **kwargs)
            
            # Preparar datos
            data = self.prepare_data(module_name, field_names, field_types)
            
            # Generar contenido
            content = self.generate_content(
                data['module_name'], 
                data['field_names'], 
                data['field_types'], 
                data=data, 
                **kwargs
            )
            
            # Obtener ruta del archivo
            file_path = self.get_file_path(data['module_name'], **kwargs)
            
            # Guardar archivo
            self.save_file(file_path, content)
            
            return {
                "success": True,
                "file_path": file_path,
                "generator_type": self.generator_type,
                "module_name": module_name
            }
            
        except ValueError as e:
            return error_handler.handle_validation_error(e, self.generator_type)
        except OSError as e:
            return error_handler.handle_file_error(e, "archivo", "generación")
        except Exception as e:
            return error_handler.handle_generation_error(e, self.generator_type, module_name)

class ModelGenerator(BaseGenerator):
    """Generador de modelos SQLAlchemy"""
    
    def __init__(self):
        super().__init__("model")
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar código del modelo"""
        from .Generar_Funciones.Generar_Models import generate_model
        return generate_model(module_name, field_names, field_types)
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener ruta del archivo de modelo"""
        return self.path_manager.get_file_path("model", module_name)

class SchemaGenerator(BaseGenerator):
    """Generador de schemas Pydantic"""
    
    def __init__(self):
        super().__init__("schema")
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar código del schema"""
        from .Generar_Funciones.Generar_Schema import generate_schema
        return generate_schema(module_name, field_names, field_types)
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener ruta del archivo de schema"""
        return self.path_manager.get_file_path("schema", module_name, "Schema_")

class CRUDGenerator(BaseGenerator):
    """Generador de funciones CRUD"""
    
    def __init__(self):
        super().__init__("crud")
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar código CRUD"""
        from .Generar_Funciones.Generar_Cruds import generate_crud_functions
        return generate_crud_functions(module_name, field_names, field_types)
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener ruta del archivo CRUD"""
        return self.path_manager.get_file_path("crud", module_name, "Crud_")

class RouteGenerator(BaseGenerator):
    """Generador de rutas FastAPI"""
    
    def __init__(self):
        super().__init__("route")
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar código de rutas"""
        from .Generar_Funciones.Generar_Routes import generate_route
        return generate_route(module_name, field_names, field_types)
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener ruta del archivo de rutas"""
        return self.path_manager.get_file_path("route", module_name, "Route_")

class HTMLGenerator(BaseGenerator):
    """Generador de formularios HTML"""
    
    def __init__(self):
        super().__init__("html")
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar código HTML"""
        from .Generar_Funciones.Generar_Html import generate_html_form
        return generate_html_form(module_name, field_names, field_types)
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener ruta del archivo HTML"""
        return self.path_manager.get_file_path("html", module_name)

class TestGenerator(BaseGenerator):
    """Generador de tests unitarios"""
    
    def __init__(self):
        super().__init__("test")
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar código de tests"""
        from .Generar_Funciones.Generar_Test import generate_tests
        return generate_tests(module_name, field_names, field_types)
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener ruta del archivo de test"""
        return self.path_manager.get_file_path("test", module_name, "test_")

class ServiceGenerator(BaseGenerator):
    """Generador de servicios completos"""
    
    def __init__(self):
        super().__init__("service")
        self.sub_generators = {
            'model': ModelGenerator(),
            'schema': SchemaGenerator(), 
            'crud': CRUDGenerator(),
            'route': RouteGenerator(),
            'html': HTMLGenerator()
        }
    
    def generate_content(self, module_name: str, field_names: List[str], 
                        field_types: List[str], **kwargs) -> str:
        """Generar servicio completo - retorna resumen"""
        return f"# Servicio completo generado para {module_name}"
    
    def get_file_path(self, module_name: str, **kwargs) -> str:
        """Obtener directorio del servicio"""
        return self.path_manager.get_service_directory(module_name)
    
    def generate_service_components(self, module_name: str, field_names: List[str], 
                                  field_types: List[str]) -> Dict[str, Any]:
        """Generar todos los componentes del servicio"""
        service_dir = self.get_file_path(module_name)
        results = {"success": True, "generated_files": [], "errors": []}
        
        with GenerationSession(module_name, "service", self.logger) as session:
            try:
                # Crear directorio del servicio
                self.path_manager.ensure_directory_exists(service_dir)
                
                # Generar componentes usando generadores específicos para servicios
                components = {
                    'service': ('Generar_Cruds_sql', 'generate_crud_functions', f'service_{module_name}.py'),
                    'route': ('Generar_Routes_service', 'generate_route', f'route_{module_name}.py'),
                    'schema': ('Generar_Schema_serice', 'generate_schema', f'schema_{module_name}.py'),
                    'model': ('Generar_Models_service', 'generate_model', f'model_{module_name}.py')
                }
                
                for comp_name, (module_path, func_name, filename) in components.items():
                    try:
                        # Importar dinámicamente la función
                        module = __import__(f'.Generar_Funciones.{module_path}', 
                                          fromlist=[func_name], level=1)
                        generate_func = getattr(module, func_name)
                        
                        # Generar contenido
                        content = generate_func(module_name, field_names, field_types)
                        
                        # Guardar archivo
                        file_path = os.path.join(service_dir, filename)
                        self.save_file(file_path, content)
                        
                        session.add_generated_file(file_path)
                        results["generated_files"].append(file_path)
                        
                    except Exception as e:
                        error_msg = f"Error generando {comp_name}: {str(e)}"
                        session.add_error(e, comp_name)
                        results["errors"].append(error_msg)
                
                # Generar __init__.py
                init_content = self.generate_init_file(module_name)
                init_path = os.path.join(service_dir, "__init__.py")
                self.save_file(init_path, init_content)
                session.add_generated_file(init_path)
                results["generated_files"].append(init_path)
                
                # Generar HTML y JS
                self.generate_html_components(module_name, field_names, field_types, session, results)
                
                # Registrar servicio
                self.register_service(module_name, session)
                
            except Exception as e:
                session.add_error(e, "servicio completo")
                results["success"] = False
                results["errors"].append(str(e))
        
        return results
    
    def generate_init_file(self, module_name: str) -> str:
        """Generar archivo __init__.py para el servicio"""
        module_name_cap = module_name.capitalize()
        return f"""# Archivo __init__.py para el servicio {module_name}
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_{module_name} import {module_name_cap}
from .schema_{module_name} import {module_name_cap}Create, {module_name_cap}Update, {module_name_cap}Read
from .service_{module_name} import (
    create_{module_name}, 
    get_{module_name}, 
    gets_{module_name},
    update_{module_name},
    delete_{module_name}
)
from .route_{module_name} import router

# Para facilitar la inclusión del router en la aplicación principal
{module_name}_router = router

__all__ = [
    '{module_name_cap}',
    '{module_name_cap}Create',
    '{module_name_cap}Update', 
    '{module_name_cap}Read',
    'create_{module_name}',
    'get_{module_name}',
    'gets_{module_name}',
    'update_{module_name}',
    'delete_{module_name}',
    'router',
    '{module_name}_router'
]
"""
    
    def generate_html_components(self, module_name: str, field_names: List[str], 
                               field_types: List[str], session: GenerationSession, 
                               results: Dict[str, Any]):
        """Generar componentes HTML y JS para el servicio"""
        try:
            from .Generar_Funciones.Generar_Html_service import generate_html_for_service
            html_content, js_content = generate_html_for_service(module_name, field_names, field_types)
            
            # Crear directorio específico para el módulo
            module_dir = f"sql_app/static/{module_name}"
            self.path_manager.ensure_directory_exists(module_dir)
            
            # Guardar HTML
            html_path = os.path.join(module_dir, "index.html")
            self.save_file(html_path, html_content)
            session.add_generated_file(html_path)
            results["generated_files"].append(html_path)
            
            # Guardar JS
            js_path = os.path.join(module_dir, f"{module_name}_service.js")
            self.save_file(js_path, js_content)
            session.add_generated_file(js_path)
            results["generated_files"].append(js_path)
            
        except Exception as e:
            session.add_error(e, "componentes HTML/JS")
            results["errors"].append(f"Error generando HTML/JS: {str(e)}")
    
    def register_service(self, module_name: str, session: GenerationSession):
        """Registrar el servicio en el gestor de servicios"""
        try:
            from routers.config import service_manager
            
            service_id = f"{module_name}.route_{module_name}"
            
            if service_manager.services_manager is None:
                session.add_warning("El gestor de servicios no está inicializado", "registro")
                return False
            
            services_manager = service_manager.services_manager
            services_manager.scan_services()
            
            if service_id not in services_manager.active_services:
                services_manager.active_services[service_id] = True
            
            success = services_manager.register_service(service_id)
            services_manager.save_state()
            
            self.logger.log_service_registration(service_id, success)
            return success
            
        except Exception as e:
            session.add_error(e, f"registro de servicio {module_name}")
            return False

class GeneratorFactory:
    """Factory para crear generadores"""
    
    _generators = {
        'model': ModelGenerator,
        'schema': SchemaGenerator,
        'crud': CRUDGenerator,
        'route': RouteGenerator,
        'html': HTMLGenerator,
        'test': TestGenerator,
        'service': ServiceGenerator
    }
    
    @classmethod
    def create_generator(cls, generator_type: str) -> BaseGenerator:
        """Crear un generador del tipo especificado"""
        if generator_type not in cls._generators:
            available = ', '.join(cls._generators.keys())
            raise ValueError(f"Tipo de generador '{generator_type}' no válido. Disponibles: {available}")
        
        return cls._generators[generator_type]()
    
    @classmethod
    def get_available_generators(cls) -> List[str]:
        """Obtener lista de generadores disponibles"""
        return list(cls._generators.keys())
    
    @classmethod
    def register_generator(cls, generator_type: str, generator_class):
        """Registrar un nuevo tipo de generador"""
        if not issubclass(generator_class, BaseGenerator):
            raise ValueError("El generador debe heredar de BaseGenerator")
        
        cls._generators[generator_type] = generator_class

# Instancia global del factory
generator_factory = GeneratorFactory()
