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
        
        # SOLO cargar el estado desde el archivo, pero NO activar servicios
        self.load_state(activate_services=False)

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

        
        # Añadir esta función para debugging
    def check_services_state(self):
        """Verifica el estado actual de los servicios y lo muestra en el log."""
        logger.info("=== Estado de los servicios ===")
        
        # Mostrar servicios activos según el estado interno
        active_services = [s for s, active in self.active_services.items() if active]
        logger.info(f"Servicios marcados como activos: {len(active_services)}")
        
        for service_id in active_services:
            is_registered = service_id in self.services
            
            # MEJORA: Verificar si realmente está registrado en app.routes
            actually_registered = False
            if is_registered and "router" in self.services[service_id]:
                router = self.services[service_id]["router"]
                actually_registered = any(getattr(route, "router", None) == router for route in self.app.routes)
            
            status = "✅ Activo y operativo" if actually_registered else "⚠️ Marcado activo pero NO operativo"
            logger.info(f"  - {service_id}: {status}")
        
        # Verificar servicios en el archivo de estado
        state_file = os.path.join(self.base_dir, 'Services', 'services_state.json')
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    import json
                    state = json.load(f)
                    services_in_file = [s for s, active in state.get('services', {}).items() if active]
                    logger.info(f"Servicios activos en archivo {state_file}: {len(services_in_file)}")
                    
                    # MEJORA: Verificar consistencia entre memoria y archivo
                    for service_id in services_in_file:
                        in_memory_active = service_id in self.active_services and self.active_services[service_id]
                        actually_registered = False
                        
                        if service_id in self.services and "router" in self.services[service_id]:
                            router = self.services[service_id]["router"]
                            actually_registered = any(getattr(route, "router", None) == router for route in self.app.routes)
                        
                        status = "✅" if in_memory_active and actually_registered else "⚠️"
                        if in_memory_active and not actually_registered:
                            status += " (marcado activo pero NO operativo)"
                        elif not in_memory_active:
                            status += " (inconsistente: activo en archivo pero NO en memoria)"
                        
                        logger.info(f"  - {service_id}: {status}")
                    
                    # MEJORA: Detectar inconsistencias
                    memory_only = [s for s in active_services if s not in services_in_file]
                    if memory_only:
                        logger.warning(f"Servicios activos en memoria pero NO en archivo: {len(memory_only)}")
                        for service_id in memory_only:
                            logger.warning(f"  - {service_id}")
                    
            except Exception as e:
                logger.error(f"Error al leer archivo de estado: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            logger.warning(f"El archivo de estado {state_file} no existe")
        
        # MEJORA: Sugerencia de corrección si hay inconsistencias
        active_but_not_working = [s for s in active_services 
                                if s in self.services and "router" in self.services[s] and 
                                not any(getattr(route, "router", None) == self.services[s]["router"] for route in self.app.routes)]
        
        if active_but_not_working:
            logger.warning("===== ATENCIÓN: SERVICIOS NO OPERATIVOS =====")
            logger.warning(f"Los siguientes servicios están marcados como activos pero no están operativos:")
            for service_id in active_but_not_working:
                logger.warning(f"  → {service_id}")
            logger.warning("Pruebe refreshing estos servicios o reinicie la aplicación")

    # Añadir este método a la clase ServicesManager (por ejemplo después del método register_all_maestros)
    def activate_saved_services(self, ask_confirmation=False):
        """Activa todos los servicios que estaban marcados como activos en el estado guardado.
        
        Args:
            ask_confirmation (bool): Si es True, retorna una lista de servicios pendientes en lugar
                                     de activarlos directamente. El código que llama debe manejar la confirmación.
        """
        # Primero escanear servicios disponibles para actualizar la lista
        available_services = self.scan_services()
        available_maestros = self.scan_maestros()
        
        # Obtener servicios que deberían activarse
        active_services = [s for s, active in self.active_services.items() if active]
        active_maestros = [m for m, active in self.active_maestros.items() if active]
        
        # Filtrar solo los disponibles
        pending_services = [s for s in active_services if s in available_services]
        pending_maestros = [m for m in active_maestros if m in available_maestros]
        
        logger.info(f"Intentando activar {len(pending_services)} servicios y {len(pending_maestros)} maestros guardados")
        
        # Si se solicita confirmación, devolver la lista de servicios y maestros pendientes
        if ask_confirmation:
            return {
                'services': pending_services,
                'maestros': pending_maestros
            }
        
        activated_services = 0
        activated_maestros = 0
        
        # Mostrar servicios que deberían activarse
        for service_id in pending_services:
            logger.info(f"  → Activando servicio: {service_id}")
        
        # Activar servicios guardados
        for service_id in pending_services:
            try:
                # Verificar si el servicio ya está realmente activado
                already_active = False
                if service_id in self.services and "router" in self.services[service_id]:
                    router = self.services[service_id]["router"]
                    already_active = any(getattr(route, "router", None) == router for route in self.app.routes)
                
                if already_active:
                    logger.info(f"Servicio {service_id} ya estaba registrado en rutas")
                    activated_services += 1
                    continue
                
                # Forzar el registro del servicio incluso si está marcado como activo
                if self.register_service(service_id, force=True):
                    activated_services += 1
                    logger.info(f"✅ Servicio {service_id} activado correctamente")
                    
                    # Verificar que realmente esté en las rutas
                    service_registered = any(
                        hasattr(route, "router") and 
                        service_id in self.services and
                        getattr(route, "router", None) == self.services[service_id].get("router")
                        for route in self.app.routes
                    )
                    
                    if not service_registered:
                        logger.warning(f"⚠️ Servicio {service_id} marcado como activo pero no está en app.routes")
                else:
                    logger.warning(f"❌ No se pudo activar el servicio {service_id}")
            except Exception as e:
                logger.error(f"❌ Error al activar servicio {service_id}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # AHORA FUERA DEL BUCLE DE SERVICIOS - Activar maestros guardados
        logger.info(f"Intentando activar {len(active_maestros)} maestros guardados:")
        
        for maestro_id in pending_maestros:
            try:
                already_included = any(
                    hasattr(route, "router") and 
                    maestro_id in self.maestros and
                    getattr(route, "router", None) == self.maestros[maestro_id].get("router")
                    for route in self.app.routes
                )
                
                if already_included:
                    logger.info(f"Maestro {maestro_id} ya estaba registrado en rutas")
                    activated_maestros += 1
                    continue
                    
                if self.register_maestro(maestro_id):
                    activated_maestros += 1
                    logger.info(f"✅ Maestro {maestro_id} activado correctamente")
                else:
                    logger.warning(f"❌ No se pudo activar el maestro {maestro_id}")
            except Exception as e:
                logger.error(f"Error al activar maestro {maestro_id}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # AHORA FUERA DE AMBOS BUCLES - Guardar estado final
        self.save_state()
        
        logger.info(f"✅ Activados {activated_services} servicios y {activated_maestros} maestros según el estado guardado")
        return activated_services + activated_maestros > 0    
    
    def import_models(self) -> bool:
        """Importa todos los modelos de servicios."""
        services_path = os.path.join(self.base_dir, "Services")
        models_imported = 0
        
        if not os.path.exists(services_path):
            logger.warning(f"El directorio de servicios {services_path} no existe.")
            return False
        
        # Recorrer el directorio de servicios de forma recursiva
        for root, _, files in os.walk(services_path):
            # Excluye carpetas específicas
            if any(excluded in root for excluded in ['__pycache__', 'security', 'tests']):
                continue
                
            # Busca archivos de modelos
            for file in files:
                if file.startswith('model_') and file.endswith('.py'):
                    # Obtiene la ruta relativa desde la carpeta Services
                    relative_path = os.path.relpath(root, services_path)
                    if relative_path == '.':  # Si está en la raíz de Services
                        module_path = file[:-3]
                    else:
                        module_path = f"{relative_path.replace(os.sep, '.')}.{file[:-3]}"
                    
                    # Ruta completa del módulo
                    full_module_path = f"Services.{module_path}"
                    
                    try:
                        if full_module_path in sys.modules:
                            importlib.reload(sys.modules[full_module_path])
                        else:
                            importlib.import_module(full_module_path)
                        logger.info(f"Modelo importado: {full_module_path}")
                        models_imported += 1
                    except Exception as e:
                        logger.error(f"Error al importar modelo {full_module_path}: {str(e)}")
        
        # Crear tablas en la base de datos
        try:
            from db.database import Base, engine
            Base.metadata.create_all(bind=engine)
            logger.info(f"Tablas creadas para {models_imported} modelos importados")
        except Exception as e:
            logger.error(f"Error al crear tablas: {str(e)}")
            return False
        
        return models_imported > 0


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
            
            # Forzar recarga del módulo
            if module_path in sys.modules:
                logger.info(f"Recargando módulo {module_path}")
                del sys.modules[module_path]  # Eliminar primero
                
            # Importar módulo fresco
            module = importlib.import_module(module_path)
            
            # Buscar el router explícitamente
            router = None
            for attr_name, attr_value in module.__dict__.items():
                if isinstance(attr_value, APIRouter):
                    router = attr_value
                    break
                    
            if not router:
                logger.error(f"No se encontró router en {module_path}")
                return None
                    
            # Guardar info del servicio
            self.services[service_id] = {
                "name": service_id.split(".")[-1],
                "router": router,
                "path": module_path,
                "router_name": attr_name if attr_name else "unknown"
            }
            
            # Verificar el router cargado
            if hasattr(router, "routes") and len(router.routes) > 0:
                route_paths = [r.path for r in router.routes]
                logger.info(f"Router de {service_id} cargado con {len(router.routes)} rutas: {route_paths}")
            else:
                logger.warning(f"Router de {service_id} cargado pero no tiene rutas definidas!")
                    
            return router
                
        except Exception as e:
            logger.error(f"Error al cargar el servicio {service_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None    
        

    def diagnose_routes(self):
        """Diagnóstico detallado de las rutas registradas en FastAPI."""
        logger.info("=== DIAGNÓSTICO DE RUTAS ===")
        
        # Listar todas las rutas en la aplicación
        logger.info(f"Total de rutas en app.routes: {len(self.app.routes)}")
        
        # Agrupar rutas por router
        routers_found = {}
        for route in self.app.routes:
            router = getattr(route, "router", None)
            if router:
                router_id = id(router)
                if router_id not in routers_found:
                    routers_found[router_id] = {
                        "router": router,
                        "routes": [],
                        "service_id": "unknown"
                    }
                routers_found[router_id]["routes"].append(route)
                
        # Mapear routers a servicios
        for service_id, service_data in self.services.items():
            if "router" in service_data:
                router_id = id(service_data["router"])
                if router_id in routers_found:
                    routers_found[router_id]["service_id"] = service_id
        
        # Mostrar diagnóstico por router
        for router_id, data in routers_found.items():
            service_id = data["service_id"]
            routes_count = len(data["routes"])
            is_active = service_id in self.active_services and self.active_services[service_id]
            
            status = "✅ Activo" if is_active else "⚠️ No activo"
            logger.info(f"Router {service_id}: {status} con {routes_count} rutas registradas")
            
            # Listar rutas
            for route in data["routes"][:3]:  # Mostrar solo las primeras 3 para no saturar logs
                logger.info(f"  - {route.path} [{route.methods}]")
            
            if len(data["routes"]) > 3:
                logger.info(f"  ... y {len(data['routes']) - 3} rutas más")
        
        # Detectar servicios activos sin rutas
        missing_routes = []
        for service_id, is_active in self.active_services.items():
            if is_active:
                # Verificar si realmente tiene rutas
                found = False
                if service_id in self.services and "router" in self.services[service_id]:
                    router = self.services[service_id]["router"]
                    for data in routers_found.values():
                        if data["router"] == router and len(data["routes"]) > 0:
                            found = True
                            break
                
                if not found:
                    missing_routes.append(service_id)
        
        if missing_routes:
            logger.warning(f"⚠️ {len(missing_routes)} servicios marcados como activos no tienen rutas:")
            for service_id in missing_routes:
                logger.warning(f"  → {service_id}")


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
    
    def unregister_maestro(self, maestro_id: str) -> bool:
        """Desregistra un maestro de la aplicación."""
        if maestro_id not in self.active_maestros or not self.active_maestros[maestro_id]:
            logger.warning(f"El maestro {maestro_id} no está activo.")
            return False
        
        try:
            # Simplemente marcar como inactivo sin intentar eliminar rutas
            self.active_maestros[maestro_id] = False
            logger.info(f"Maestro {maestro_id} marcado como inactivo.")
            return True
        except Exception as e:
            logger.error(f"Error al desregistrar el maestro {maestro_id}: {str(e)}")
            return False
        
    # En el método register_service, añadir esto después de cargar el router:
    def register_service(self, service_id: str, force=False) -> bool:
        """Registra un servicio en la aplicación."""
        # Si debemos forzar el registro, usamos refresh_service que es más seguro
        if force:
            return self.refresh_service(service_id)

            
        # Si no estamos forzando, verificar si ya está activo
        if service_id in self.active_services and self.active_services[service_id]:
            # Verificar si realmente está en app.routes
            already_registered = False
            if service_id in self.services and "router" in self.services[service_id]:
                router = self.services[service_id]["router"]
                already_registered = any(getattr(route, "router", None) == router for route in self.app.routes)
            
            if already_registered:
                logger.warning(f"El servicio {service_id} ya está activo y operativo.")
                return False
            else:
                logger.warning(f"El servicio {service_id} está marcado como activo pero no es operativo. Forzando registro.")
                return self.refresh_service(service_id)
        
        # Si no está activo, procedemos con el registro normal
        router = self.load_service(service_id)
        if router:
            try:
                # Intentar importar el modelo asociado y crear tablas
                model_module_name = service_id.replace("route_", "model_")
                try:
                    module_path = f"Services.{model_module_name}"
                    if module_path in sys.modules:
                        importlib.reload(sys.modules[module_path])
                    else:
                        importlib.import_module(module_path)
                    
                    # Crear tablas después de importar el modelo
                    from db.database import Base, engine
                    Base.metadata.create_all(bind=engine)
                    logger.info(f"Tablas para {service_id} creadas correctamente")
                except ImportError:
                    logger.info(f"No se encontró modelo para {service_id}, continuando")
                except Exception as model_error:
                    logger.warning(f"Error al cargar modelo para {service_id}: {str(model_error)}")
                
                # Registrar el router normalmente sin intentar eliminar rutas anteriores
                self.app.include_router(router)
                self.active_services[service_id] = True
                
                # Verificar que realmente se registró
                service_registered = any(
                    getattr(route, "router", None) == router
                    for route in self.app.routes
                )
                
                if service_registered:
                    logger.info(f"✅ Servicio {service_id} registrado correctamente y verificado en app.routes")
                else:
                    logger.warning(f"⚠️ Problema: El servicio {service_id} no se detectó en app.routes después del registro")
                
                # Guardar estado
                self.save_state()
                return True
            except Exception as e:
                logger.error(f"Error al registrar el servicio {service_id}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        return False
    
    def unregister_service(self, service_id: str) -> bool:
        """Desregistra un servicio de la aplicación."""
        if service_id not in self.active_services or not self.active_services[service_id]:
            logger.warning(f"El servicio {service_id} no está activo.")
            return False
        
        try:
            # Simplemente marcar como inactivo sin intentar eliminar rutas
            # Las rutas se sobreescribirán la próxima vez que se registre el servicio
            self.active_services[service_id] = False
            logger.info(f"Servicio {service_id} marcado como inactivo.")
            
            # Guardar estado actualizado
            self.save_state()
            return True
        except Exception as e:
            logger.error(f"Error al desregistrar el servicio {service_id}: {str(e)}")
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
        """Refresca un servicio correctamente para FastAPI."""
        try:
            # Recargar el módulo para obtener una versión fresca del router
            module_path = f"Services.{service_id}"
            if module_path in sys.modules:
                del sys.modules[module_path]  # Eliminar completamente de sys.modules
            
            # Cargar el módulo nuevamente
            router = self.load_service(service_id)
            if not router:
                logger.error(f"❌ No se pudo cargar el servicio {service_id}")
                return False
            
            # Registrar el router en FastAPI
            try:
                self.app.include_router(router)
                self.active_services[service_id] = True
                
                # Verificación explícita
                for route in self.app.routes:
                    if hasattr(route, "router") and route.router == router:
                        logger.info(f"✅ Ruta verificada para {service_id}: {route.path}")
                
                # Guardar estado
                self.save_state()
                return True
            except Exception as register_error:
                logger.error(f"Error al registrar router: {str(register_error)}")
                return False
                
        except Exception as e:
            logger.error(f"Error en refresh_service para {service_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
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

    def save_state(self):
        """Guarda el estado de activación en un archivo."""
        state_file = os.path.join(self.base_dir, 'Services', 'services_state.json')
        
        # Primero verificar qué servicios están realmente activos
        active_count = sum(1 for s, active in self.active_services.items() if active)
        logger.info(f"Guardando estado de {active_count} servicios activos")
        
        try:
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(state_file), exist_ok=True)
            
            # Preparar el estado para guardar
            state = {
                'services': self.active_services,
                'maestros': self.active_maestros
            }
            
            # Mostrar información de debug
            for service_id, is_active in self.active_services.items():
                if is_active:
                    logger.info(f"  → Guardando servicio activo: {service_id}")
            
            # Guardar el estado como JSON
            with open(state_file, 'w') as f:
                import json
                json.dump(state, f, indent=4)
            
            # Verificar que el archivo se guardó correctamente
            if os.path.exists(state_file):
                logger.info(f"✓ Estado guardado exitosamente en {state_file}")
                return True
            else:
                logger.error(f"✗ No se pudo guardar el archivo {state_file}")
                return False
        except Exception as e:
            logger.error(f"Error al guardar estado: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def load_state(self, activate_services=True):
        """Carga el estado de activación desde un archivo."""
        state_file = os.path.join(self.base_dir, 'Services', 'services_state.json')
        if not os.path.exists(state_file):
            logger.warning(f"Archivo de estado no encontrado: {state_file}")
            # Crear archivo de estado vacío
            try:
                empty_state = {
                    'services': {},
                    'maestros': {}
                }
                os.makedirs(os.path.dirname(state_file), exist_ok=True)
                with open(state_file, 'w') as f:
                    import json
                    json.dump(empty_state, f, indent=4)
                logger.info(f"Creado nuevo archivo de estado en {state_file}")
            except Exception as e:
                logger.error(f"Error al crear archivo de estado: {str(e)}")
            return False
        
        try:
            with open(state_file, 'r') as f:
                import json
                state = json.load(f)
                
                # Mostrar los servicios activos cargados
                if 'services' in state:
                    active_services = [s for s, active in state['services'].items() if active]
                    logger.info(f"Cargado estado: {len(active_services)} servicios activos")
                    for service_id in active_services:
                        logger.info(f"  → Servicio activo cargado: {service_id}")
                    
                    # Cargar el estado en memoria
                    self.active_services = state['services']
                    
                    # IMPORTANTE: Solo activar servicios si se solicita explícitamente
                    if activate_services:
                        logger.info("Activando servicios desde load_state...")
                        self.activate_saved_services()
                else:
                    self.active_services = {}
                    logger.warning("No se encontraron servicios en el archivo de estado")
                
                if 'maestros' in state:
                    self.active_maestros = state['maestros']
                else:
                    self.active_maestros = {}
                    
                logger.info(f"Estado de servicios cargado desde {state_file}")
                return True
        except Exception as e:
            logger.error(f"Error al cargar estado de servicios: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False