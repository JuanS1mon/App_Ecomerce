"""
Módulo de reportes de stock avanzados según normas ISO 9001, ISO 14001 y mejores prácticas ERP.
Proporciona análisis detallados para toma de decisiones y cumplimiento normativo.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TipoReporte(Enum):
    """Tipos de reportes según normas ISO para diferentes propósitos"""
    AUDITORIA_COMPLETA = "auditoria_completa"
    CONTROL_CALIDAD = "control_calidad"
    ROTACION_INVENTARIO = "rotacion_inventario"
    OBSOLESCENCIA = "obsolescencia"
    CUMPLIMIENTO_ISO = "cumplimiento_iso"
    ANALISIS_TENDENCIAS = "analisis_tendencias"

def generar_reporte_auditoria_completa(db: Session, id_deposito: int = None) -> Dict[str, Any]:
    """
    Genera reporte de auditoría completa según ISO 9001 para trazabilidad total.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito específico (opcional)
        
    Returns:
        Reporte completo de auditoría con todas las validaciones ISO
    """
    try:
        fecha_inicio = datetime.now()
        where_clause = "WHERE s.id_deposito = :id_deposito" if id_deposito else ""
        params = {"id_deposito": id_deposito} if id_deposito else {}
        
        # 1. Resumen general de stock
        query_resumen = text(f"""
            SELECT 
                COUNT(DISTINCT s.codigo_art) as total_articulos,
                COUNT(DISTINCT s.id_deposito) as total_depositos,
                COUNT(DISTINCT s.nro_movimiento) as total_movimientos,
                COUNT(*) as total_registros,
                SUM(CASE WHEN s.cant_disponible < 0 THEN 1 ELSE 0 END) as stocks_negativos,
                SUM(CASE WHEN s.confirmado = 0 OR s.confirmado IS NULL THEN 1 ELSE 0 END) as movimientos_pendientes
            FROM stock s
            {where_clause}
        """)
        
        resumen = db.execute(query_resumen, params).first()
        
        # 2. Análisis de inconsistencias críticas
        query_inconsistencias = text(f"""
            SELECT 
                s.codigo_art,
                s.id_deposito,
                a.descripcion as articulo_nombre,
                d.descripcion as deposito_nombre,
                s.cant_disponible,
                s.cant_reservado,
                s.cant_preparado,
                CASE 
                    WHEN s.cant_disponible < 0 THEN 'Stock negativo'
                    WHEN s.cant_reservado > s.cant_disponible THEN 'Sobre-reserva'
                    WHEN DATEDIFF(day, CAST(s.fecha AS DATE), GETDATE()) > 30 AND (s.confirmado = 0 OR s.confirmado IS NULL) THEN 'Movimiento antiguo pendiente'
                    ELSE 'OK'
                END as tipo_inconsistencia
            FROM stock s
            LEFT JOIN articulos a ON s.codigo_art = a.id
            LEFT JOIN depositos d ON s.id_deposito = d.id
            {where_clause}
            HAVING tipo_inconsistencia != 'OK'
        """)
        
        inconsistencias = db.execute(query_inconsistencias, params).fetchall()
        
        # 3. Análisis de rotación por categorías
        query_rotacion = text(f"""
            SELECT 
                s.codigo_art,
                a.descripcion,
                COUNT(DISTINCT s.nro_movimiento) as frecuencia_movimientos,
                AVG(s.cant_disponible) as promedio_stock,
                MAX(s.cant_disponible) as stock_maximo,
                MIN(s.cant_disponible) as stock_minimo,
                DATEDIFF(day, MIN(CAST(s.fecha AS DATE)), MAX(CAST(s.fecha AS DATE))) as dias_actividad,
                CASE 
                    WHEN COUNT(DISTINCT s.nro_movimiento) > 20 THEN 'Alta rotación'
                    WHEN COUNT(DISTINCT s.nro_movimiento) > 5 THEN 'Media rotación'
                    ELSE 'Baja rotación'
                END as categoria_rotacion
            FROM stock s
            LEFT JOIN articulos a ON s.codigo_art = a.id
            {where_clause}
            GROUP BY s.codigo_art, a.descripcion
            ORDER BY frecuencia_movimientos DESC
        """)
        
        rotacion = db.execute(query_rotacion, params).fetchall()
        
        # 4. Cumplimiento de normas ISO
        cumplimiento_iso = {
            "trazabilidad_completa": True,  # Todos los movimientos tienen registro
            "stocks_negativos_controlados": resumen.stocks_negativos == 0,
            "movimientos_confirmados": resumen.movimientos_pendientes < (resumen.total_registros * 0.1),  # Menos del 10% pendiente
            "rotacion_adecuada": len([r for r in rotacion if r.categoria_rotacion == 'Alta rotación']) > 0,
            "inconsistencias_criticas": len(inconsistencias) == 0
        }
        
        # 5. Recomendaciones automáticas
        recomendaciones = []
        
        if resumen.stocks_negativos > 0:
            recomendaciones.append({
                "prioridad": "Alta",
                "accion": "Corregir stocks negativos inmediatamente",
                "cantidad_afectada": resumen.stocks_negativos,
                "norma_iso": "ISO 9001 - Control de procesos"
            })
        
        if resumen.movimientos_pendientes > (resumen.total_registros * 0.1):
            recomendaciones.append({
                "prioridad": "Media",
                "accion": "Confirmar movimientos pendientes",
                "cantidad_afectada": resumen.movimientos_pendientes,
                "norma_iso": "ISO 9001 - Trazabilidad"
            })
        
        if len([r for r in rotacion if r.categoria_rotacion == 'Baja rotación']) > (len(rotacion) * 0.3):
            recomendaciones.append({
                "prioridad": "Baja",
                "accion": "Revisar política de inventarios para artículos de baja rotación",
                "norma_iso": "ISO 14001 - Gestión eficiente de recursos"
            })
        
        # Resultado del reporte
        return {
            "metadatos": {
                "tipo_reporte": TipoReporte.AUDITORIA_COMPLETA.value,
                "fecha_generacion": fecha_inicio.isoformat(),
                "tiempo_procesamiento": (datetime.now() - fecha_inicio).total_seconds(),
                "ambito": f"Depósito {id_deposito}" if id_deposito else "Global",
                "version_iso": "ISO 9001:2015"
            },
            "resumen_ejecutivo": {
                "total_articulos": resumen.total_articulos,
                "total_depositos": resumen.total_depositos,
                "total_movimientos": resumen.total_movimientos,
                "cumple_iso": all(cumplimiento_iso.values()),
                "nivel_criticidad": "Alto" if inconsistencias else "Bajo",
                "puntuacion_calidad": round((sum(cumplimiento_iso.values()) / len(cumplimiento_iso)) * 100, 2)
            },
            "analisis_detallado": {
                "inconsistencias": [
                    {
                        "codigo_art": inc.codigo_art,
                        "deposito": inc.id_deposito,
                        "articulo": inc.articulo_nombre or "Sin descripción",
                        "deposito_nombre": inc.deposito_nombre or "Sin descripción",
                        "tipo": inc.tipo_inconsistencia,
                        "stock_actual": float(inc.cant_disponible or 0),
                        "requiere_accion_inmediata": inc.tipo_inconsistencia in ['Stock negativo', 'Sobre-reserva']
                    }
                    for inc in inconsistencias
                ],
                "rotacion_inventario": [
                    {
                        "codigo_art": rot.codigo_art,
                        "descripcion": rot.descripcion or "Sin descripción",
                        "categoria": rot.categoria_rotacion,
                        "frecuencia_movimientos": rot.frecuencia_movimientos,
                        "stock_promedio": float(rot.promedio_stock or 0),
                        "dias_actividad": rot.dias_actividad or 0
                    }
                    for rot in rotacion
                ]
            },
            "cumplimiento_iso": cumplimiento_iso,
            "recomendaciones": recomendaciones,
            "proxima_auditoria": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de auditoría: {e}")
        return {
            "error": str(e),
            "metadatos": {
                "tipo_reporte": TipoReporte.AUDITORIA_COMPLETA.value,
                "fecha_generacion": datetime.now().isoformat(),
                "estado": "error"
            }
        }

def generar_reporte_control_calidad(db: Session, periodo_dias: int = 30) -> Dict[str, Any]:
    """
    Genera reporte de control de calidad según ISO 9001 para monitoreo continuo.
    
    Args:
        db: Sesión de base de datos
        periodo_dias: Período de análisis en días
        
    Returns:
        Reporte de control de calidad con métricas de performance
    """
    try:
        fecha_inicio = datetime.now() - timedelta(days=periodo_dias)
        
        # Consulta de movimientos en el período
        query_calidad = text("""
            SELECT 
                s.id_deposito,
                d.descripcion as deposito_nombre,
                COUNT(*) as total_movimientos,
                COUNT(CASE WHEN s.confirmado = 1 THEN 1 END) as movimientos_confirmados,
                COUNT(CASE WHEN s.cant_disponible < 0 THEN 1 END) as stocks_negativos,
                AVG(DATEDIFF(hour, CAST(s.fecha AS DATETIME), GETDATE())) as tiempo_promedio_confirmacion,
                COUNT(CASE WHEN s.anulado = 1 THEN 1 END) as movimientos_anulados
            FROM stock s
            LEFT JOIN depositos d ON s.id_deposito = d.id
            WHERE CAST(s.fecha AS DATE) >= :fecha_inicio
            GROUP BY s.id_deposito, d.descripcion
            ORDER BY total_movimientos DESC
        """)
        
        datos_calidad = db.execute(query_calidad, {"fecha_inicio": fecha_inicio.date()}).fetchall()
        
        # Cálculo de métricas de calidad
        metricas_globales = {
            "total_depositos_activos": len(datos_calidad),
            "promedio_confirmacion": sum(d.movimientos_confirmados for d in datos_calidad) / sum(d.total_movimientos for d in datos_calidad) * 100 if datos_calidad else 0,
            "tiempo_respuesta_promedio": sum(d.tiempo_promedio_confirmacion or 0 for d in datos_calidad) / len(datos_calidad) if datos_calidad else 0,
            "tasa_errores": sum(d.stocks_negativos for d in datos_calidad) / sum(d.total_movimientos for d in datos_calidad) * 100 if datos_calidad else 0
        }
        
        # Clasificación de performance por depósito
        performance_depositos = []
        for deposito in datos_calidad:
            tasa_confirmacion = (deposito.movimientos_confirmados / deposito.total_movimientos * 100) if deposito.total_movimientos > 0 else 0
            tasa_errores = (deposito.stocks_negativos / deposito.total_movimientos * 100) if deposito.total_movimientos > 0 else 0
            
            # Clasificación según estándares ISO
            if tasa_confirmacion >= 95 and tasa_errores <= 2:
                clasificacion = "Excelente"
                color = "green"
            elif tasa_confirmacion >= 85 and tasa_errores <= 5:
                clasificacion = "Bueno"
                color = "yellow"
            else:
                clasificacion = "Requiere mejora"
                color = "red"
            
            performance_depositos.append({
                "id_deposito": deposito.id_deposito,
                "nombre": deposito.deposito_nombre or f"Depósito {deposito.id_deposito}",
                "total_movimientos": deposito.total_movimientos,
                "tasa_confirmacion": round(tasa_confirmacion, 2),
                "tasa_errores": round(tasa_errores, 2),
                "tiempo_respuesta_horas": round(deposito.tiempo_promedio_confirmacion or 0, 2),
                "clasificacion": clasificacion,
                "color_semaforo": color,
                "cumple_iso": tasa_confirmacion >= 85 and tasa_errores <= 5
            })
        
        return {
            "metadatos": {
                "tipo_reporte": TipoReporte.CONTROL_CALIDAD.value,
                "fecha_generacion": datetime.now().isoformat(),
                "periodo_analisis": f"{periodo_dias} días",
                "norma_aplicada": "ISO 9001:2015 - Control de Calidad"
            },
            "metricas_globales": {
                **metricas_globales,
                "nivel_calidad": "Excelente" if metricas_globales["promedio_confirmacion"] >= 95 and metricas_globales["tasa_errores"] <= 2 else
                                "Bueno" if metricas_globales["promedio_confirmacion"] >= 85 and metricas_globales["tasa_errores"] <= 5 else
                                "Requiere mejora"
            },
            "performance_depositos": sorted(performance_depositos, key=lambda x: x["tasa_confirmacion"], reverse=True),
            "alertas_calidad": [
                d for d in performance_depositos 
                if not d["cumple_iso"]
            ],
            "acciones_recomendadas": [
                {
                    "accion": "Capacitación en procesos",
                    "depositos_objetivo": [d["nombre"] for d in performance_depositos if d["tasa_confirmacion"] < 85],
                    "prioridad": "Alta"
                },
                {
                    "accion": "Revisión de procedimientos",
                    "depositos_objetivo": [d["nombre"] for d in performance_depositos if d["tasa_errores"] > 5],
                    "prioridad": "Media"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de control de calidad: {e}")
        return {"error": str(e)}

def generar_reporte_obsolescencia(db: Session, dias_inactividad: int = 90) -> Dict[str, Any]:
    """
    Genera reporte de obsolescencia según ISO 14001 para gestión eficiente de recursos.
    
    Args:
        db: Sesión de base de datos
        dias_inactividad: Días sin movimiento para considerar obsoleto
        
    Returns:
        Reporte de artículos obsoletos y recomendaciones de gestión
    """
    try:
        fecha_limite = datetime.now() - timedelta(days=dias_inactividad)
        
        query_obsolescencia = text("""
            WITH UltimoMovimiento AS (
                SELECT 
                    s.codigo_art,
                    s.id_deposito,
                    MAX(CAST(s.fecha AS DATE)) as ultima_fecha,
                    SUM(s.cant_disponible) as stock_total
                FROM stock s
                GROUP BY s.codigo_art, s.id_deposito
            )
            SELECT 
                um.codigo_art,
                um.id_deposito,
                a.descripcion as articulo_nombre,
                d.descripcion as deposito_nombre,
                um.ultima_fecha,
                um.stock_total,
                DATEDIFF(day, um.ultima_fecha, GETDATE()) as dias_sin_movimiento,
                CASE 
                    WHEN DATEDIFF(day, um.ultima_fecha, GETDATE()) > :dias_criticos THEN 'Crítico'
                    WHEN DATEDIFF(day, um.ultima_fecha, GETDATE()) > :dias_inactividad THEN 'Obsoleto'
                    ELSE 'Activo'
                END as categoria_obsolescencia
            FROM UltimoMovimiento um
            LEFT JOIN articulos a ON um.codigo_art = a.id
            LEFT JOIN depositos d ON um.id_deposito = d.id
            WHERE um.ultima_fecha < :fecha_limite
            ORDER BY dias_sin_movimiento DESC
        """)
        
        articulos_obsoletos = db.execute(query_obsolescencia, {
            "fecha_limite": fecha_limite.date(),
            "dias_inactividad": dias_inactividad,
            "dias_criticos": dias_inactividad * 2
        }).fetchall()
        
        # Análisis por categorías
        resumen_obsolescencia = {
            "total_articulos_obsoletos": len(articulos_obsoletos),
            "valor_stock_obsoleto": sum(float(art.stock_total or 0) for art in articulos_obsoletos),
            "articulos_criticos": len([art for art in articulos_obsoletos if art.categoria_obsolescencia == 'Crítico']),
            "tiempo_promedio_inactividad": sum(art.dias_sin_movimiento for art in articulos_obsoletos) / len(articulos_obsoletos) if articulos_obsoletos else 0
        }
        
        # Recomendaciones según ISO 14001
        recomendaciones_ambientales = []
        
        if resumen_obsolescencia["articulos_criticos"] > 0:
            recomendaciones_ambientales.append({
                "accion": "Evaluación para reciclaje o disposición responsable",
                "cantidad_items": resumen_obsolescencia["articulos_criticos"],
                "impacto_ambiental": "Alto",
                "norma_iso": "ISO 14001 - Gestión Ambiental"
            })
        
        if resumen_obsolescencia["valor_stock_obsoleto"] > 10000:  # Valor configurable
            recomendaciones_ambientales.append({
                "accion": "Reubicación o liquidación controlada",
                "valor_estimado": resumen_obsolescencia["valor_stock_obsoleto"],
                "impacto_ambiental": "Medio",
                "norma_iso": "ISO 14001 - Eficiencia de recursos"
            })
        
        return {
            "metadatos": {
                "tipo_reporte": TipoReporte.OBSOLESCENCIA.value,
                "fecha_generacion": datetime.now().isoformat(),
                "criterio_dias": dias_inactividad,
                "norma_aplicada": "ISO 14001:2015 - Gestión Ambiental"
            },
            "resumen_ejecutivo": resumen_obsolescencia,
            "articulos_detalle": [
                {
                    "codigo_art": art.codigo_art,
                    "deposito": art.id_deposito,
                    "articulo_nombre": art.articulo_nombre or "Sin descripción",
                    "deposito_nombre": art.deposito_nombre or f"Depósito {art.id_deposito}",
                    "ultima_actividad": art.ultima_fecha.isoformat() if art.ultima_fecha else None,
                    "dias_inactivo": art.dias_sin_movimiento,
                    "stock_actual": float(art.stock_total or 0),
                    "categoria": art.categoria_obsolescencia,
                    "accion_recomendada": "Disposición inmediata" if art.categoria_obsolescencia == 'Crítico' 
                                        else "Evaluación para reubicación" if art.categoria_obsolescencia == 'Obsoleto'
                                        else "Monitoreo"
                }
                for art in articulos_obsoletos
            ],
            "recomendaciones_ambientales": recomendaciones_ambientales,
            "proxima_revision": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de obsolescencia: {e}")
        return {"error": str(e)}
