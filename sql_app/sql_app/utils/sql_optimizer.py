# =============================
# SQL QUERY OPTIMIZER
# =============================
# Utilidades para optimización de consultas SQL

from sqlalchemy import Index, text
from sqlalchemy.orm import Session
from sql_app.db.database import engine
from sql_app.db.models import *
import logging
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger("sql_optimizer")

class QueryOptimizer:
    """Optimizador de consultas SQL"""
    
    def __init__(self):
        self.performance_stats = {}
    
    async def create_performance_indexes(self):
        """Crea índices para mejorar el rendimiento"""
        try:
            logger.info("🔧 Creando índices de rendimiento...")
            
            # Usar conexión directa para DDL
            with engine.connect() as conn:
                
                # Índices para movements (consultas más frecuentes)
                indexes_to_create = [
                    # Movements - búsquedas por fecha y estado
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_movements_fecha_estado ON movements(fecha, estado) INCLUDE (cantidad, observaciones)",
                    
                    # Movements - búsquedas por OT
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_movements_ot_id_fecha ON movements(ot_id, fecha) INCLUDE (cantidad, tipo_movimiento)",
                    
                    # Movements - búsquedas por ubicación
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_movements_location_id_fecha ON movements(location_id, fecha DESC)",
                    
                    # OTs - búsquedas por estado y fecha
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_ots_estado_fecha ON ots(estado, fecha_inicio) INCLUDE (titulo, descripcion)",
                    
                    # OTs - búsquedas por institución
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_ots_institution_id_estado ON ots(institution_id, estado)",
                    
                    # Users - búsquedas por email y estado
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_users_email_active ON users(email, is_active) INCLUDE (username, role)",
                    
                    # Locations - búsquedas por institución
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_locations_institution_id ON locations(institution_id) INCLUDE (nombre, tipo)",
                    
                    # Artworks - búsquedas por artista y estado
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_artworks_artist_id_estado ON artworks(artist_id, estado) INCLUDE (titulo, fecha_creacion)",
                    
                    # Auth tokens - búsquedas por usuario y expiración
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_auth_tokens_user_expiry ON auth_tokens(user_id, expires_at) WHERE is_revoked = 0",
                    
                    # Activity logs - búsquedas por usuario y fecha
                    "CREATE NONCLUSTERED INDEX IF NOT EXISTS IX_activity_logs_user_fecha ON activity_logs(user_id, timestamp DESC)"
                ]
                
                created_count = 0
                for index_sql in indexes_to_create:
                    try:
                        conn.execute(text(index_sql))
                        created_count += 1
                        logger.info(f"✅ Índice creado: {index_sql.split('IX_')[1].split(' ')[0] if 'IX_' in index_sql else 'unknown'}")
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(f"⚠️ Error creando índice: {e}")
                        # Si ya existe, es normal
                
                conn.commit()
                logger.info(f"📊 Índices procesados: {created_count}/{len(indexes_to_create)}")
                
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
            raise
    
    def get_query_stats(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Obtiene estadísticas de una consulta"""
        try:
            with engine.connect() as conn:
                # Obtener plan de ejecución
                explain_query = f"SET SHOWPLAN_ALL ON; {query}; SET SHOWPLAN_ALL OFF;"
                
                start_time = time.time()
                result = conn.execute(text(query), params or {})
                execution_time = time.time() - start_time
                
                return {
                    "execution_time": execution_time,
                    "rows_affected": result.rowcount if hasattr(result, 'rowcount') else 0,
                    "query_hash": hash(query)
                }
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats de consulta: {e}")
            return {"error": str(e)}
    
    async def optimize_common_queries(self):
        """Optimiza consultas comunes del sistema"""
        logger.info("🚀 Optimizando consultas comunes...")
        
        # Definir consultas optimizadas para casos comunes
        optimized_queries = {
            "movements_by_ot": """
                SELECT m.id, m.fecha, m.cantidad, m.tipo_movimiento, m.observaciones,
                       l.nombre as location_name, l.tipo as location_type
                FROM movements m WITH (NOLOCK)
                INNER JOIN locations l ON m.location_id = l.id
                WHERE m.ot_id = :ot_id
                ORDER BY m.fecha DESC
            """,
            
            "active_ots_by_institution": """
                SELECT o.id, o.titulo, o.descripcion, o.estado, o.fecha_inicio,
                       i.nombre as institution_name
                FROM ots o WITH (NOLOCK)
                INNER JOIN institutions i ON o.institution_id = i.id
                WHERE o.estado IN ('activo', 'en_proceso')
                  AND i.id = :institution_id
                ORDER BY o.fecha_inicio DESC
            """,
            
            "user_recent_activity": """
                SELECT TOP 50 al.action, al.details, al.timestamp, al.ip_address
                FROM activity_logs al WITH (NOLOCK)
                WHERE al.user_id = :user_id
                  AND al.timestamp >= DATEADD(day, -30, GETDATE())
                ORDER BY al.timestamp DESC
            """,
            
            "movements_summary_by_location": """
                SELECT l.id, l.nombre, l.tipo,
                       COUNT(m.id) as total_movements,
                       SUM(CASE WHEN m.tipo_movimiento = 'entrada' THEN m.cantidad ELSE 0 END) as total_entradas,
                       SUM(CASE WHEN m.tipo_movimiento = 'salida' THEN m.cantidad ELSE 0 END) as total_salidas
                FROM locations l WITH (NOLOCK)
                LEFT JOIN movements m ON l.id = m.location_id 
                  AND m.fecha >= :fecha_desde
                WHERE l.institution_id = :institution_id
                GROUP BY l.id, l.nombre, l.tipo
                ORDER BY total_movements DESC
            """
        }
        
        # Almacenar para uso posterior
        self.optimized_queries = optimized_queries
        logger.info(f"✅ {len(optimized_queries)} consultas optimizadas preparadas")
    
    def get_optimized_query(self, query_name: str) -> Optional[str]:
        """Obtiene una consulta optimizada por nombre"""
        return getattr(self, 'optimized_queries', {}).get(query_name)
    
    async def analyze_slow_queries(self):
        """Analiza consultas lentas en el sistema"""
        try:
            logger.info("🔍 Analizando consultas lentas...")
            
            with engine.connect() as conn:
                # Query para encontrar consultas lentas en SQL Server
                slow_query_analysis = text("""
                    SELECT TOP 10
                        qs.sql_handle,
                        qs.execution_count,
                        qs.total_elapsed_time / qs.execution_count AS avg_elapsed_time,
                        qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
                        qs.total_physical_reads / qs.execution_count AS avg_physical_reads,
                        SUBSTRING(st.text, (qs.statement_start_offset/2) + 1,
                            ((CASE WHEN qs.statement_end_offset = -1
                                THEN LEN(CONVERT(nvarchar(max), st.text)) * 2
                                ELSE qs.statement_end_offset
                            END - qs.statement_start_offset)/2) + 1) AS query_text
                    FROM sys.dm_exec_query_stats AS qs
                    CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
                    WHERE st.text LIKE '%movements%' OR st.text LIKE '%ots%'
                    ORDER BY avg_elapsed_time DESC
                """)
                
                result = conn.execute(slow_query_analysis)
                slow_queries = result.fetchall()
                
                if slow_queries:
                    logger.info(f"📊 Encontradas {len(slow_queries)} consultas para optimización")
                    for idx, query in enumerate(slow_queries[:3]):  # Top 3
                        logger.info(f"🐌 Query lenta #{idx+1}: {query.avg_elapsed_time:.2f}ms promedio")
                else:
                    logger.info("✅ No se encontraron consultas significativamente lentas")
                    
        except Exception as e:
            logger.warning(f"⚠️ No se pudo analizar consultas lentas: {e}")
    
    async def update_table_statistics(self):
        """Actualiza estadísticas de tablas para mejor rendimiento"""
        try:
            logger.info("📈 Actualizando estadísticas de tablas...")
            
            tables = [
                'movements', 'ots', 'users', 'locations', 
                'institutions', 'artworks', 'auth_tokens', 'activity_logs'
            ]
            
            with engine.connect() as conn:
                for table in tables:
                    try:
                        update_stats_sql = f"UPDATE STATISTICS {table} WITH FULLSCAN"
                        conn.execute(text(update_stats_sql))
                        logger.info(f"✅ Estadísticas actualizadas para: {table}")
                    except Exception as e:
                        logger.warning(f"⚠️ Error actualizando stats de {table}: {e}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error actualizando estadísticas: {e}")

# =============================
# UTILIDADES DE OPTIMIZACIÓN
# =============================

class ConnectionOptimizer:
    """Optimizador de conexiones de base de datos"""
    
    @staticmethod
    def get_connection_pool_stats():
        """Obtiene estadísticas del pool de conexiones"""
        try:
            pool = engine.pool
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total_connections": pool.checkedin() + pool.checkedout()
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats del pool: {e}")
            return {}
    
    @staticmethod
    async def optimize_connection_settings():
        """Optimiza configuraciones de conexión"""
        try:
            with engine.connect() as conn:
                # Configuraciones de optimización para SQL Server
                optimizations = [
                    "SET ARITHABORT ON",
                    "SET CONCAT_NULL_YIELDS_NULL ON", 
                    "SET QUOTED_IDENTIFIER ON",
                    "SET ANSI_NULLS ON"
                ]
                
                for opt in optimizations:
                    conn.execute(text(opt))
                
                logger.info("⚡ Configuraciones de conexión optimizadas")
                
        except Exception as e:
            logger.warning(f"⚠️ Error optimizando conexiones: {e}")

# =============================
# INICIALIZACIÓN
# =============================

# Instancia global del optimizador
query_optimizer = QueryOptimizer()
connection_optimizer = ConnectionOptimizer()

async def init_sql_optimizations():
    """Inicializa todas las optimizaciones SQL"""
    logger.info("🚀 Inicializando optimizaciones SQL...")
    
    try:
        # Crear índices de rendimiento
        await query_optimizer.create_performance_indexes()
        
        # Preparar consultas optimizadas
        await query_optimizer.optimize_common_queries()
        
        # Optimizar configuraciones de conexión
        await connection_optimizer.optimize_connection_settings()
        
        # Actualizar estadísticas
        await query_optimizer.update_table_statistics()
        
        # Analizar consultas lentas
        await query_optimizer.analyze_slow_queries()
        
        logger.info("✅ Optimizaciones SQL completadas")
        
    except Exception as e:
        logger.error(f"❌ Error en optimizaciones SQL: {e}")
        raise
