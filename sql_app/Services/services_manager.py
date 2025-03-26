import os
import sys
import importlib
import importlib.util
import inspect
from typing import Dict, List, Optional, Any
import logging
from fastapi import FastAPI, APIRouter

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("services_manager")

class ServicesManager:
    def __init__(self, app: FastAPI):
        self.app = app
        self.services: Dict[str, Dict[str, Any]] = {}
        self.maestros: Dict[str, Dict[str, Any]] = {}
        self.active_services: Dict[str, bool] = {}
        self.active_maestros: Dict[str, bool] = {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info(f"Directorio base: {self.base_dir}")

    def scan_services(self) -> List[str]:
        """Escanea el directorio de servicios y detecta los módulos que comienzan con route_."""
        services = []
        services_path = os.path.join(self.base_dir, "Services")
        
        if not os.path.exists(services_path):
            logger.warning(f"El directorio de servicios {services_path} no existe.")
            return services
        
        # Recorre el directorio de servicios de forma recursiva
        for root, _, files in os.walk(services_path):
            # Excluye carpetas específicas que no deben considerarse servicios
            if any(excluded in root for excluded in ['__pycache__', 'security', 'tests']):
                continue
                
            # Busca archivos de rutas
            for file in files:
                if file.startswith('route_') and file.endswith('.py'):
                    # Obtiene la ruta relativa desde la carpeta Services
                    relative_path = os.path.relpath(root, services_path)
                    if relative_path == '.':  # Si está en la raíz de Services
                        module_path = file[:-3]
                    else:
                        module_path = f"{relative_path.replace(os.sep, '.')}.{file[:-3]}"
                    
                    service_id = module_path
                    services.append(service_id)
                    logger.info(f"Servicio detectado: {service_id} en {os.path.join(root, file)}")
        
        return services
    
    def scan_maestros(self) -> List[str]:
        """Escanea el directorio de maestros y detecta los módulos disponibles."""
        maestros = []
        maestros_path = os.path.join(self.base_dir, "routers", "Maestros")
        
        if not os.path.exists(maestros_path):
            logger.warning(f"El directorio de maestros {maestros_path} no existe.")
            return maestros
        
        # Busca archivos que comiencen con Route_ o route_
        for file in os.listdir(maestros_path):
            if (file.startswith('Route_') or file.startswith('route_')) and file.endswith('.py'):
                maestro_id = file[:-3]
                maestros.append(maestro_id)
                logger.info(f"Maestro detectado: {maestro_id}")
        
        return maestros
    
    def load_service(self, service_id: str) -> Optional[APIRouter]:
        """Carga un servicio por su ID."""
        try:
            # Construye la ruta del módulo
            module_path = f"Services.{service_id}"
            
            # Si ya está en cache, recargarlo
            if module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)
            
            # Busca el router en el módulo
            for attr_name, attr_value in module.__dict__.items():
                if isinstance(attr_value, APIRouter):
                    # Guarda información sobre el servicio
                    self.services[service_id] = {
                        "name": service_id.split(".")[-1],
                        "router": attr_value,
                        "path": module_path,
                        "router_name": attr_name
                    }
                    
                    logger.info(f"Servicio {service_id} cargado exitosamente.")
                    return attr_value
            
            logger.warning(f"No se encontró un router en el módulo {module_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error al cargar el servicio {service_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def load_maestro(self, maestro_id: str) -> Optional[APIRouter]:
        """Carga un maestro por su ID."""
        try:
            module_path = f"routers.Maestros.{maestro_id}"
            
            # Si ya está en cache, recargarlo
            if module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)
            
            # Busca el router en el módulo
            for attr_name, attr_value in module.__dict__.items():
                if isinstance(attr_value, APIRouter):
                    # Guarda información sobre el maestro
                    prefix = "Route_" if maestro_id.startswith("Route_") else "route_"
                    name = maestro_id[len(prefix):] if maestro_id.startswith(prefix) else maestro_id
                    
                    self.maestros[maestro_id] = {
                        "name": name,
                        "router": attr_value,
                        "path": module_path,
                        "router_name": attr_name
                    }
                    
                    logger.info(f"Maestro {maestro_id} cargado exitosamente.")
                    return attr_value
            
            logger.warning(f"No se encontró un router en el módulo {module_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error al cargar el maestro {maestro_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def register_service(self, service_id: str) -> bool:
        """Registra un servicio en la aplicación."""
        if service_id in self.active_services and self.active_services[service_id]:
            logger.warning(f"El servicio {service_id} ya está activo.")
            return False
        
        router = self.load_service(service_id)
        if router:
            try:
                self.app.include_router(router)
                self.active_services[service_id] = True
                logger.info(f"Servicio {service_id} registrado correctamente.")
                return True
            except Exception as e:
                logger.error(f"Error al registrar el servicio {service_id}: {str(e)}")
                return False
        return False
    
    def register_maestro(self, maestro_id: str) -> bool:
        """Registra un maestro en la aplicación."""
        if maestro_id in self.active_maestros and self.active_maestros[maestro_id]:
            logger.warning(f"El maestro {maestro_id} ya está activo.")
            return False
        
        router = self.load_maestro(maestro_id)
        if router:
            try:
                self.app.include_router(router)
                self.active_maestros[maestro_id] = True
                logger.info(f"Maestro {maestro_id} registrado correctamente.")
                return True
            except Exception as e:
                logger.error(f"Error al registrar el maestro {maestro_id}: {str(e)}")
                return False
        return False
    
    def unregister_service(self, service_id: str) -> bool:
        """Desregistra un servicio de la aplicación."""
        if service_id not in self.active_services or not self.active_services[service_id]:
            logger.warning(f"El servicio {service_id} no está activo.")
            return False
        
        try:
            # Encuentra el router en la app
            if service_id in self.services:
                router = self.services[service_id]["router"]
                # Remove router from app.routes
                self.app.routes = [route for route in self.app.routes 
                                 if getattr(route, "router", None) != router]
                self.active_services[service_id] = False
                logger.info(f"Servicio {service_id} desregistrado correctamente.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al desregistrar el servicio {service_id}: {str(e)}")
            return False
    
    def unregister_maestro(self, maestro_id: str) -> bool:
        """Desregistra un maestro de la aplicación."""
        if maestro_id not in self.active_maestros or not self.active_maestros[maestro_id]:
            logger.warning(f"El maestro {maestro_id} no está activo.")
            return False
        
        try:
            # Encuentra el router en la app
            if maestro_id in self.maestros:
                router = self.maestros[maestro_id]["router"]
                # Remove router from app.routes
                self.app.routes = [route for route in self.app.routes 
                                 if getattr(route, "router", None) != router]
                self.active_maestros[maestro_id] = False
                logger.info(f"Maestro {maestro_id} desregistrado correctamente.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al desregistrar el maestro {maestro_id}: {str(e)}")
            return False
    
    def register_all_services(self) -> Dict[str, bool]:
        """Registra todos los servicios disponibles."""
        results = {}
        services = self.scan_services()
        
        for service_id in services:
            results[service_id] = self.register_service(service_id)
        
        return results
    
    def register_all_maestros(self) -> Dict[str, bool]:
        """Registra todos los maestros disponibles."""
        results = {}
        maestros = self.scan_maestros()
        
        for maestro_id in maestros:
            results[maestro_id] = self.register_maestro(maestro_id)
        
        return results
    
    def refresh_service(self, service_id: str) -> bool:
        """Refresca un servicio (lo desregistra y lo vuelve a registrar)."""
        was_active = service_id in self.active_services and self.active_services[service_id]
        
        if was_active:
            self.unregister_service(service_id)
        
        return self.register_service(service_id)
    
    def refresh_maestro(self, maestro_id: str) -> bool:
        """Refresca un maestro (lo desregistra y lo vuelve a registrar)."""
        was_active = maestro_id in self.active_maestros and self.active_maestros[maestro_id]
        
        if was_active:
            self.unregister_maestro(maestro_id)
        
        return self.register_maestro(maestro_id)
    
    def get_service_info(self, service_id: str) -> Dict[str, Any]:
        """Obtiene información sobre un servicio específico."""
        if service_id in self.services:
            info = self.services[service_id].copy()
            info["active"] = self.active_services.get(service_id, False)
            # Eliminar la referencia circular del router para serializar
            if "router" in info:
                del info["router"]
            return info
        return {"error": f"Servicio {service_id} no encontrado"}
    
    def get_maestro_info(self, maestro_id: str) -> Dict[str, Any]:
        """Obtiene información sobre un maestro específico."""
        if maestro_id in self.maestros:
            info = self.maestros[maestro_id].copy()
            info["active"] = self.active_maestros.get(maestro_id, False)
            # Eliminar la referencia circular del router para serializar
            if "router" in info:
                del info["router"]
            return info
        return {"error": f"Maestro {maestro_id} no encontrado"}
    
    def get_all_services_info(self) -> List[Dict[str, Any]]:
        """Obtiene información sobre todos los servicios."""
        services_info = []
        for service_id in self.services:
            services_info.append(self.get_service_info(service_id))
        return services_info
    
    def get_all_maestros_info(self) -> List[Dict[str, Any]]:
        """Obtiene información sobre todos los maestros."""
        maestros_info = []
        for maestro_id in self.maestros:
            maestros_info.append(self.get_maestro_info(maestro_id))
        return maestros_info