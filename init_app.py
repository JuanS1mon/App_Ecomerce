import os
import importlib
import logging
import traceback
import glob
import sys


def discover_and_import_service_models(logger=None):
    """
    Descubre e importa automáticamente todos los modelos de los servicios en Services/
    Busca archivos model_*.py en la estructura: Services/service_name/table_name/model_table_name.py
    
    Returns:
        int: Número de modelos importados exitosamente
    """
    imported_count = 0
    services_dir = "Services"
    
    if not os.path.exists(services_dir):
        if logger:
            logger.info(f"📁 Directorio {services_dir} no existe, saltando descubrimiento de modelos de servicios")
        return 0
    
    try:
        # Buscar todos los archivos model_*.py en Services/
        model_pattern = os.path.join(services_dir, "**", "model_*.py")
        model_files = glob.glob(model_pattern, recursive=True)
        
        if logger:
            logger.info(f"Descubriendo modelos en Services/... encontrados {len(model_files)} archivos")
        
        for model_file in model_files:
            try:
                # Convertir ruta de archivo a módulo Python
                # Ejemplo: Services/app_studio/tabla_1/model_tabla_1.py -> Services.app_studio.tabla_1.model_tabla_1
                relative_path = os.path.relpath(model_file)
                module_path = relative_path.replace(os.sep, '.').replace('.py', '')
                
                # Importar el módulo dinámicamente
                importlib.import_module(module_path)
                imported_count += 1
                
                if logger:
                    logger.info(f"  Modelo importado: {module_path}")
                    
            except Exception as e:
                if logger:
                    logger.warning(f"  No se pudo importar {model_file}: {str(e)}")
        
        if logger:
            logger.info(f"Total de modelos de servicios importados: {imported_count}")
        
        return imported_count
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error al descubrir modelos de servicios: {e}")
        return imported_count


def create_all_tables(create_tables_func, logger=None):
    try:
        # 1. Importar modelos esenciales del sistema
        if logger:
            logger.info("Importando modelos del sistema...")
            
        known_models = [
            'db.models.config.usuarios',
            'db.models.config.roles',
        ]
        
        system_models_count = 0
        for module_name in known_models:
            try:
                importlib.import_module(module_name)
                system_models_count += 1
            except ImportError as e:
                if logger:
                    logger.warning(f"  No se pudo importar el modelo {module_name}: {e}")
        
        if logger:
            logger.info(f"Modelos del sistema importados: {system_models_count}/{len(known_models)}")
        
        # 2. Importar modelos de ecommerce
        if logger:
            logger.info("Importando modelos de ecommerce...")
        
        ecommerce_models = [
            'Projects.ecomerce.models.categorias',
            'Projects.ecomerce.models.productos',
            'Projects.ecomerce.models.carritos',
            'Projects.ecomerce.models.carrito_items',
            'Projects.ecomerce.models.pedidos',
            'Projects.ecomerce.models.presupuestos',
            'Projects.ecomerce.models.stock',
        ]
        
        ecommerce_models_count = 0
        for module_name in ecommerce_models:
            try:
                importlib.import_module(module_name)
                ecommerce_models_count += 1
                if logger:
                    logger.info(f"  Modelo ecommerce importado: {module_name}")
            except ImportError as e:
                if logger:
                    logger.warning(f"  No se pudo importar el modelo ecommerce {module_name}: {e}")
        
        if logger:
            logger.info(f"Modelos de ecommerce importados: {ecommerce_models_count}/{len(ecommerce_models)}")
        
        # 3. Descubrir e importar modelos de servicios generados
        if logger:
            logger.info("Descubriendo modelos de servicios en Services/...")
        
        service_models_count = discover_and_import_service_models(logger)
        
        # 4. Crear todas las tablas
        if logger:
            logger.info("Creando tablas en la base de datos...")
        
        create_tables_func()
        
        if logger:
            total_models = system_models_count + ecommerce_models_count + service_models_count
            logger.info(f"Tablas creadas/verificadas exitosamente ({total_models} modelos)")
            
    except Exception as e:
        if logger:
            logger.error(f"❌ Error al crear tablas: {e}")
        traceback.print_exc()

def ensure_directories():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        os.path.join(base_dir, "Services"),
        os.path.join(base_dir, "routers", "Maestros")
    ]
    for directory in directories:
        if not os.path.exists(directory):
            logging.getLogger("main").info(f"Creando directorio: {directory}")
            os.makedirs(directory, exist_ok=True)
