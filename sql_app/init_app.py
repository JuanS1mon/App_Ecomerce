import os
import importlib
import logging
import traceback

def create_all_tables(create_tables_func, logger=None):
    try:
        known_models = [
            'sql_app.db.models.config.usuarios',
            'sql_app.db.models.config.tickets',
        ]
        for module_name in known_models:
            try:
                importlib.import_module(module_name)
                # if logger:
                #     logger.info(f"Modelo importado: {module_name}")
            except ImportError as e:
                if logger:
                    logger.warning(f"No se pudo importar el modelo {module_name}: {e}")
        create_tables_func()
        # if logger:
        #     logger.info("Tablas creadas exitosamente")
    except Exception as e:
        if logger:
            logger.error(f"Error al crear tablas: {e}")
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
