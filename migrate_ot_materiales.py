"""
Script de migración manual para crear la tabla ot_materiales
Ejecutar desde la raíz del proyecto: python migrate_ot_materiales.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sql_app.config import get_database_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_ot_materiales_table():
    """Crear la tabla ot_materiales"""
    
    # Obtener URL de la base de datos
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    # SQL para crear la tabla
    create_table_sql = """
    CREATE TABLE ot_materiales (
        id INTEGER IDENTITY(1,1) PRIMARY KEY,
        ot_id INTEGER NOT NULL,
        codigo_art INTEGER NOT NULL,
        id_deposito INTEGER NOT NULL,
        cantidad_planificada FLOAT DEFAULT 0.0,
        cantidad_utilizada FLOAT DEFAULT 0.0,
        cantidad_devuelta FLOAT DEFAULT 0.0,
        estado NVARCHAR(20) DEFAULT 'planificado',
        fecha_planificacion DATETIME DEFAULT GETDATE(),
        fecha_consumo DATETIME NULL,
        fecha_devolucion DATETIME NULL,
        observacion NTEXT NULL,
        usuario_consumo NVARCHAR(100) NULL,
        nro_movimiento_stock INTEGER NULL,
        
        -- Foreign Keys
        CONSTRAINT FK_ot_materiales_ot FOREIGN KEY (ot_id) REFERENCES ot(id) ON DELETE CASCADE,
        CONSTRAINT FK_ot_materiales_deposito FOREIGN KEY (id_deposito) REFERENCES depositos(id)
    );
    """
    
    # SQL para crear índices
    create_indexes_sql = [
        "CREATE INDEX IX_ot_materiales_ot_id ON ot_materiales(ot_id);",
        "CREATE INDEX IX_ot_materiales_codigo_art ON ot_materiales(codigo_art);",
        "CREATE INDEX IX_ot_materiales_deposito ON ot_materiales(id_deposito);",
        "CREATE INDEX IX_ot_materiales_estado ON ot_materiales(estado);",
        "CREATE INDEX IX_ot_materiales_ot_articulo_deposito ON ot_materiales(ot_id, codigo_art, id_deposito);"
    ]
    
    try:
        with engine.connect() as conn:
            # Verificar si la tabla ya existe
            check_table = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'ot_materiales'
            """)).fetchone()
            
            if check_table.count > 0:
                logger.info("La tabla ot_materiales ya existe")
                return True
            
            # Crear la tabla
            logger.info("Creando tabla ot_materiales...")
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("Tabla ot_materiales creada exitosamente")
            
            # Crear índices
            logger.info("Creando índices...")
            for index_sql in create_indexes_sql:
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error al crear índice: {e}")
            
            logger.info("Índices creados exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"Error al crear la tabla ot_materiales: {e}")
        return False

def test_ot_materiales_table():
    """Probar operaciones básicas en la tabla ot_materiales"""
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Insertar datos de prueba
            logger.info("Insertando datos de prueba...")
            
            # Primero verificar que exista al menos una OT
            ot_exists = conn.execute(text("SELECT TOP 1 id FROM ot")).fetchone()
            
            if not ot_exists:
                logger.warning("No hay OTs en la base de datos para probar")
                return False
            
            ot_id = ot_exists.id
            
            # Insertar material de prueba
            insert_sql = """
            INSERT INTO ot_materiales 
            (ot_id, codigo_art, id_deposito, cantidad_planificada, estado, observacion)
            VALUES 
            (:ot_id, 1001, 1, 10.0, 'planificado', 'Material de prueba para testing')
            """
            
            conn.execute(text(insert_sql), {"ot_id": ot_id})
            conn.commit()
            logger.info("Datos de prueba insertados")
            
            # Consultar datos
            select_sql = "SELECT * FROM ot_materiales WHERE ot_id = :ot_id"
            result = conn.execute(text(select_sql), {"ot_id": ot_id}).fetchall()
            
            logger.info(f"Datos encontrados: {len(result)} registros")
            for row in result:
                logger.info(f"Material ID: {row.id}, Artículo: {row.codigo_art}, Cantidad: {row.cantidad_planificada}")
            
            # Limpiar datos de prueba
            logger.info("Limpiando datos de prueba...")
            conn.execute(text("DELETE FROM ot_materiales WHERE observacion = 'Material de prueba para testing'"))
            conn.commit()
            
            logger.info("Prueba completada exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"Error en las pruebas: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Iniciando migración de ot_materiales ===")
    
    # Crear tabla
    if create_ot_materiales_table():
        logger.info("✅ Tabla creada exitosamente")
        
        # Probar tabla
        if test_ot_materiales_table():
            logger.info("✅ Pruebas completadas exitosamente")
        else:
            logger.error("❌ Falló en las pruebas")
    else:
        logger.error("❌ Falló al crear la tabla")
    
    logger.info("=== Migración completada ===")
