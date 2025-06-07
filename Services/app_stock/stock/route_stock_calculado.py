from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime, timedelta
try:
    from ....db.database import get_db
except ImportError:
    from sql_app.db.database import get_db
    get_top_articulos_por_stock
)


# Configurar logger
logger = logging.getLogger(__name__)

# Configurar templates
templates = Jinja2Templates(directory="sql_app/static")

# Crear router para stock calculado
router = APIRouter(
    prefix="/stock/calculado",
    tags=["stock_calculado"],
    responses={404: {"description": "No encontrado"}}
)
@router.get("/pagina", response_class=HTMLResponse)
async def get_stock_calculado_page(request: Request, db: Session = Depends(get_db)):
    """
    Devuelve la página HTML para el módulo de stock calculado en tiempo real.
    """
    try:
        # Leer el archivo HTML directamente como contenido estático
        
        # Construir la ruta del archivo HTML
        html_file_path = os.path.join("static", "app_stock", "stock", "stock_calculado.html")
        
        # Verificar si el archivo existe
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"El archivo HTML no existe en: {html_file_path}")
        
        # Leer el contenido del archivo
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Devolver el HTML directamente sin procesamiento de Jinja2
        return HTMLResponse(content=html_content, status_code=200)
        
    except FileNotFoundError as e:
        logger.error(f"Archivo HTML no encontrado: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Archivo no encontrado</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>Archivo HTML no encontrado</h1>
                <p>No se pudo encontrar el archivo: {html_file_path}</p>
                <p>Por favor, verifique que el archivo existe en la ruta correcta.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=404)
        
    except Exception as e:
        logger.error(f"Error al obtener la página de stock calculado: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Stock Calculado</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>Error al cargar la página</h1>
                <p>No se pudo cargar el módulo de stock calculado.</p>
                <p>Error: {str(e)}</p>
                <p>Por favor, contacte al administrador del sistema.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)
    
@router.get("/deposito/{id_deposito}/{codigo_art}", response_model=Dict[str, Any])
async def get_stock_calculado(
    id_deposito: int,
    codigo_art: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el stock calculado en tiempo real para un artículo en un depósito específico,
    con desglose detallado de las cantidades (enfoque SAP).
    
    Args:
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        db: Sesión de base de datos
      Returns:
        Diccionario con información detallada del stock
    """
    try:
        # Calcular el stock disponible
        stock_info = calcular_stock_disponible(db, id_deposito, codigo_art)
        
        # Obtener información usando los servicios
        articulo_info = get_articulo_info(db, codigo_art)
        deposito_info = get_deposito_info(db, id_deposito)
        
        # Construir respuesta
        result = {
            "id_deposito": id_deposito,
            "deposito_nombre": deposito_info["descripcion"],
            "codigo_art": codigo_art,
            "articulo_nombre": articulo_info["descripcion"],
            "stock": stock_info
        }
        
        return result
    except Exception as e:
        logger.error(f"Error al obtener stock calculado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular el stock: {str(e)}"
        )

@router.get("/deposito/{id_deposito}", response_model=List[Dict[str, Any]])
async def get_stock_deposito_calculado(
    id_deposito: int,
    min_disponible: Optional[float] = Query(None, description="Filtrar por cantidad mínima disponible"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el stock calculado en tiempo real para todos los artículos en un depósito específico.
    
    Args:
        id_deposito: ID del depósito
        min_disponible: Filtro opcional para mostrar solo artículos con disponibilidad >= valor
        db: Sesión de base de datos
        
    Returns:
        Lista de artículos con su stock calculado
    """
    try:
        # Obtener todos los artículos distintos en el depósito usando el servicio
        articulos_codigos = get_articulos_distintos_en_deposito(db, id_deposito)
        
        # Obtener información de todos los artículos en lote
        articulos_info = get_articulos_info_batch(db, articulos_codigos)
        
        # Calcular el stock para cada artículo
        result = []
        for codigo_art in articulos_codigos:
            stock_info = calcular_stock_disponible(db, id_deposito, codigo_art)
            
            # Aplicar filtro de disponibilidad mínima si está especificado
            if min_disponible is not None and stock_info["disponible"] < min_disponible:
                continue
                  # Obtener información del artículo del lote
            articulo_descripcion = articulos_info.get(codigo_art, f"Artículo {codigo_art}")
            
            # Agregar a los resultados
            result.append({
                "id_deposito": id_deposito,
                "codigo_art": codigo_art,
                "articulo_nombre": articulo_descripcion,
                "stock": stock_info
            })
        
        # Ordenar resultados por disponibilidad (mayor a menor)
        result.sort(key=lambda x: x["stock"]["disponible"], reverse=True)
        
        return result
    except Exception as e:
        logger.error(f"Error al obtener stock calculado del depósito: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular el stock del depósito: {str(e)}"
        )

@router.get("/articulo/{codigo_art}", response_model=Dict[str, Any])
async def get_stock_articulo_calculado(
    codigo_art: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el stock calculado en tiempo real para un artículo en todos los depósitos.
    
    Args:
        codigo_art: Código del artículo
        db: Sesión de base de datos
        
    Returns:
        Lista de depósitos con el stock calculado para el artículo
    """
    try:
        # Obtener todos los depósitos distintos que tienen este artículo usando el servicio
        depositos_ids = get_depositos_distintos_con_articulo(db, codigo_art)
          # Obtener información del artículo y depósitos usando los servicios
        articulo_info = get_articulo_info(db, codigo_art)
        depositos_info = get_depositos_info_batch(db, depositos_ids)
        
        # Calcular el stock para cada depósito
        result = []
        for id_deposito in depositos_ids:
            stock_info = calcular_stock_disponible(db, id_deposito, codigo_art)
            
            # Obtener información del depósito del lote (depositos_info ya es un dict)
            deposito_descripcion = depositos_info.get(id_deposito, f"Depósito {id_deposito}")
            
            # Agregar a los resultados
            result.append({
                "id_deposito": id_deposito,
                "deposito_nombre": deposito_descripcion,
                "stock": stock_info
            })
        
        # Ordenar resultados por disponibilidad (mayor a menor)
        result.sort(key=lambda x: x["stock"]["disponible"], reverse=True)
        
        # Calcular totales globales
        totales = {
            "fisico": sum(r["stock"]["fisico"] for r in result),
            "reservado": sum(r["stock"]["reservado"] for r in result),
            "preparado": sum(r["stock"]["preparado"] for r in result),
            "bloqueado": sum(r["stock"]["bloqueado"] for r in result),
            "disponible": sum(r["stock"]["disponible"] for r in result)
        }
        
        # Construir respuesta
        response = {
            "codigo_art": codigo_art,
            "articulo_nombre": articulo_info["descripcion"],
            "depositos": result,
            "totales": totales
        }
        
        return response
    except Exception as e:
        logger.error(f"Error al obtener stock calculado del artículo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular el stock del artículo: {str(e)}"
        )

@router.get("/comparar/{id_deposito}/{codigo_art}", response_model=Dict[str, Any])
async def comparar_stock_calculado_vs_almacenado(
    id_deposito: int,
    codigo_art: int,
    incluir_auditoria: bool = Query(False, description="Incluir información de auditoría ISO"),
    db: Session = Depends(get_db)
):
    """
    Compara el stock almacenado con el stock calculado en tiempo real,
    mostrando las diferencias según el enfoque SAP ERP y normas ISO 9001.
    
    Args:
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        incluir_auditoria: Si incluir validaciones ISO y metadatos de auditoría
        db: Sesión de base de datos
    
    Returns:
        Diccionario con la comparación detallada y validaciones ISO
    """
    try:        # Obtener stock calculado con opción de auditoría
        stock_calculado = calcular_stock_disponible(db, id_deposito, codigo_art, incluir_auditoria)
        
        # Obtener stock almacenado (último registro) usando el servicio
        stock_almacenado = get_ultimo_stock_almacenado(db, id_deposito, codigo_art)
        
        # Calcular diferencias
        diferencias = {
            "fisico": stock_calculado["fisico"] - stock_almacenado["fisico"],
            "reservado": stock_calculado["reservado"] - stock_almacenado["reservado"],
            "preparado": stock_calculado["preparado"] - stock_almacenado["preparado"],
            "bloqueado": stock_calculado["bloqueado"] - stock_almacenado["bloqueado"],
            "disponible": stock_calculado["disponible"] - stock_almacenado["fisico"]  # Comparar disponible calculado con físico almacenado
        }
        
        # Análisis de diferencias significativas (ISO 9001 - Control de calidad)
        diferencias_significativas = []
        umbral_significativo = 0.01  # 1% de diferencia es significativa
        
        for campo, diferencia in diferencias.items():
            if abs(diferencia) > umbral_significativo:
                porcentaje = (diferencia / stock_almacenado.get(campo, stock_almacenado["fisico"]) * 100) if stock_almacenado.get(campo, stock_almacenado["fisico"]) != 0 else 0
                diferencias_significativas.append({
                    "campo": campo,
                    "diferencia": diferencia,
                    "porcentaje": porcentaje,
                    "critico": abs(porcentaje) > 10  # Más del 10% es crítico
                })
        
        # Obtener información adicional del artículo y depósito usando los servicios
        articulo_info = get_articulo_info(db, codigo_art)
        deposito_info = get_deposito_info(db, id_deposito)
          # Construir respuesta
        result = {
            "id_deposito": id_deposito,
            "deposito_nombre": deposito_info["descripcion"],
            "codigo_art": codigo_art,
            "articulo_nombre": articulo_info["descripcion"],
            "stock_calculado": stock_calculado,
            "stock_almacenado": stock_almacenado,
            "diferencias": diferencias,
            "analisis_diferencias": {
                "diferencias_significativas": diferencias_significativas,
                "requiere_ajuste": len(diferencias_significativas) > 0,
                "criticidad": "alta" if any(d["critico"] for d in diferencias_significativas) else "media" if diferencias_significativas else "baja"
            },
            "fecha_comparacion": datetime.now().isoformat()
        }
        
        # Agregar validación ISO si se solicita
        if incluir_auditoria:
            from .stock_movimientos import validar_consistencia_stock
            validacion = validar_consistencia_stock(db, id_deposito, codigo_art)
            result["validacion_iso"] = validacion
        
        return result
    except Exception as e:
        logger.error(f"Error al comparar stock calculado vs almacenado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al comparar el stock: {str(e)}"
        )


@router.get("/depositos", response_model=List[Dict[str, Any]])
async def get_depositos_para_stock(db: Session = Depends(get_db)):
    """
    Obtiene la lista de depósitos disponibles para consultas de stock.
    """
    try:
        # Obtener depósitos que tienen stock usando el servicio
        depositos = get_depositos_con_stock_activo(db)
        return depositos
    except Exception as e:
        logger.error(f"Error al obtener depósitos: {e}")
        # Devolver depósitos de ejemplo en caso de error
        return [
            {"id": 1, "descripcion": "Depósito Principal"},
            {"id": 2, "descripcion": "Depósito Secundario"},
            {"id": 3, "descripcion": "Depósito Auxiliar"}
        ]

@router.get("/auditoria/{id_deposito}/{codigo_art}", response_model=Dict[str, Any])
async def get_auditoria_stock(
    id_deposito: int,
    codigo_art: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene auditoría completa del stock según normas ISO 9001 para trazabilidad.
    Incluye validaciones de consistencia, alertas de calidad y metadatos de control.
    
    Args:
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        db: Sesión de base de datos
    
    Returns:
        Diccionario con auditoría completa del stock
    """
    try:
        # Importar las nuevas funciones
        from .stock_movimientos import calcular_stock_disponible, validar_consistencia_stock
        
        # Obtener stock con auditoría completa
        stock_auditoria = calcular_stock_disponible(db, id_deposito, codigo_art, incluir_auditoria=True)
          # Validar consistencia según ISO 9001
        validacion = validar_consistencia_stock(db, id_deposito, codigo_art)
        
        # Obtener información adicional del artículo y depósito usando los servicios
        articulo_info = get_articulo_info(db, codigo_art)
        deposito_info = get_deposito_info(db, id_deposito)
        
        # Construir respuesta de auditoría
        result = {
            "id_deposito": id_deposito,
            "deposito_nombre": deposito_info["descripcion"],
            "codigo_art": codigo_art,
            "articulo_nombre": articulo_info["descripcion"],
            "stock_calculado": stock_auditoria,
            "validacion_iso": validacion,
            "resumen_auditoria": {
                "cumple_normas_iso": validacion["cumple_iso"] and stock_auditoria.get("metadatos", {}).get("cumple_iso", True),
                "requiere_atencion": len(validacion.get("inconsistencias", [])) > 0,
                "alertas_activas": len(stock_auditoria.get("metadatos", {}).get("alertas_calidad", [])),
                "fecha_auditoria": datetime.now().isoformat()
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"Error en auditoría de stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en auditoría de stock: {str(e)}"
        )

@router.get("/analisis-abc/{id_deposito}", response_model=Dict[str, Any])
async def get_analisis_abc_deposito(
    id_deposito: int,
    db: Session = Depends(get_db)
):
    """
    Análisis ABC del stock en un depósito específico según normas de gestión 
    de inventarios para optimización de recursos.
    
    Args:
        id_deposito: ID del depósito
        db: Sesión de base de datos
    
    Returns:
        Clasificación ABC de artículos por importancia
    """
    try:
        from .stock_movimientos import calcular_stock_abc
          # Realizar análisis ABC para el depósito
        analisis = calcular_stock_abc(db, id_deposito)
        
        # Obtener información del depósito usando el servicio
        deposito_info = get_deposito_info(db, id_deposito)
        
        # Construir respuesta
        result = {
            "id_deposito": id_deposito,
            "deposito_nombre": deposito_info["descripcion"],
            "analisis_abc": analisis,
            "recomendaciones": {
                "categoria_a": "Monitoreo diario - Stock crítico",
                "categoria_b": "Monitoreo semanal - Stock importante", 
                "categoria_c": "Monitoreo mensual - Stock básico"
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"Error en análisis ABC: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en análisis ABC: {str(e)}"
        )

@router.get("/analisis-abc", response_model=Dict[str, Any])
async def get_analisis_abc_global(db: Session = Depends(get_db)):
    """
    Análisis ABC global de todos los depósitos según normas de gestión 
    de inventarios para optimización de recursos a nivel empresa.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Clasificación ABC global de artículos por importancia
    """
    try:
        from .stock_movimientos import calcular_stock_abc
        
        # Realizar análisis ABC global
        analisis = calcular_stock_abc(db)
        
        # Construir respuesta
        result = {
            "ambito": "global",
            "analisis_abc": analisis,
            "recomendaciones": {
                "categoria_a": "Control estricto - Revisar diariamente",
                "categoria_b": "Control normal - Revisar semanalmente", 
                "categoria_c": "Control básico - Revisar mensualmente"
            },
            "acciones_sugeridas": {
                "categoria_a": [
                    "Implementar stock de seguridad",
                    "Monitoreo en tiempo real",
                    "Proveedores alternativos"
                ],
                "categoria_b": [
                    "Revisión periódica de stocks",
                    "Optimización de compras"
                ],
                "categoria_c": [
                    "Compras por lotes",
                    "Reducción de costos de almacenamiento"
                ]
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"Error en análisis ABC global: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en análisis ABC global: {str(e)}"
        )

@router.get("/reportes/auditoria-completa", response_model=Dict[str, Any])
async def get_reporte_auditoria_completa(
    id_deposito: Optional[int] = Query(None, description="ID del depósito específico"),
    db: Session = Depends(get_db)
):
    """
    Genera reporte de auditoría completa según normas ISO 9001 para trazabilidad total
    y cumplimiento normativo en gestión de inventarios.
    
    Args:
        id_deposito: ID del depósito específico (opcional, si no se especifica es global)
        db: Sesión de base de datos
    
    Returns:
        Reporte completo de auditoría con validaciones ISO
    """
    try:
        from .stock_reportes_iso import generar_reporte_auditoria_completa
        
        reporte = generar_reporte_auditoria_completa(db, id_deposito)
        
        return {
            "success": True,
            "reporte": reporte,
            "mensaje": f"Reporte de auditoría generado exitosamente para {'depósito ' + str(id_deposito) if id_deposito else 'todos los depósitos'}"
        }
    except Exception as e:
        logger.error(f"Error generando reporte de auditoría: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte de auditoría: {str(e)}"
        )

@router.get("/reportes/control-calidad", response_model=Dict[str, Any])
async def get_reporte_control_calidad(
    periodo_dias: int = Query(30, description="Período de análisis en días"),
    db: Session = Depends(get_db)
):
    """
    Genera reporte de control de calidad según ISO 9001 para monitoreo continuo
    del rendimiento y cumplimiento de procesos.
    
    Args:
        periodo_dias: Período de análisis en días (por defecto 30 días)
        db: Sesión de base de datos
    
    Returns:
        Reporte de control de calidad con métricas de performance
    """
    try:
        from .stock_reportes_iso import generar_reporte_control_calidad
        
        reporte = generar_reporte_control_calidad(db, periodo_dias)
        
        return {
            "success": True,
            "reporte": reporte,
            "mensaje": f"Reporte de control de calidad generado para los últimos {periodo_dias} días"
        }
    except Exception as e:
        logger.error(f"Error generando reporte de control de calidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte de control de calidad: {str(e)}"
        )

@router.get("/reportes/obsolescencia", response_model=Dict[str, Any])
async def get_reporte_obsolescencia(
    dias_inactividad: int = Query(90, description="Días sin movimiento para considerar obsoleto"),
    db: Session = Depends(get_db)
):
    """
    Genera reporte de obsolescencia según ISO 14001 para gestión eficiente de recursos
    y minimización del impacto ambiental por stock inactivo.
    
    Args:
        dias_inactividad: Días sin movimiento para considerar artículo obsoleto
        db: Sesión de base de datos
    
    Returns:
        Reporte de artículos obsoletos con recomendaciones ambientales
    """
    try:
        from .stock_reportes_iso import generar_reporte_obsolescencia
        
        reporte = generar_reporte_obsolescencia(db, dias_inactividad)
        
        return {
            "success": True,
            "reporte": reporte,
            "mensaje": f"Reporte de obsolescencia generado con criterio de {dias_inactividad} días de inactividad"
        }
    except Exception as e:
        logger.error(f"Error generando reporte de obsolescencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte de obsolescencia: {str(e)}"
        )

@router.get("/dashboard-iso", response_model=Dict[str, Any])
async def get_dashboard_iso(db: Session = Depends(get_db)):
    """
    Dashboard ejecutivo con indicadores clave de cumplimiento ISO 9001 e ISO 14001
    para monitoreo gerencial de la gestión de inventarios.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Dashboard con KPIs de cumplimiento normativo
    """
    try:
        from .stock_reportes_iso import generar_reporte_auditoria_completa, generar_reporte_control_calidad, generar_reporte_obsolescencia
        
        # Generar reportes base para el dashboard
        auditoria = generar_reporte_auditoria_completa(db)
        calidad = generar_reporte_control_calidad(db, 30)
        obsolescencia = generar_reporte_obsolescencia(db, 90)
        
        # KPIs principales
        kpis = {
            "cumplimiento_iso_9001": {
                "puntuacion": auditoria.get("resumen_ejecutivo", {}).get("puntuacion_calidad", 0),
                "estado": "Excelente" if auditoria.get("resumen_ejecutivo", {}).get("puntuacion_calidad", 0) >= 95 else
                         "Bueno" if auditoria.get("resumen_ejecutivo", {}).get("puntuacion_calidad", 0) >= 85 else
                         "Requiere mejora",
                "indicador": "green" if auditoria.get("resumen_ejecutivo", {}).get("puntuacion_calidad", 0) >= 95 else
                           "yellow" if auditoria.get("resumen_ejecutivo", {}).get("puntuacion_calidad", 0) >= 85 else
                           "red"
            },
            "eficiencia_procesos": {
                "tasa_confirmacion": calidad.get("metricas_globales", {}).get("promedio_confirmacion", 0),
                "tiempo_respuesta": calidad.get("metricas_globales", {}).get("tiempo_respuesta_promedio", 0),
                "tasa_errores": calidad.get("metricas_globales", {}).get("tasa_errores", 0)
            },
            "gestion_ambiental": {
                "articulos_obsoletos": obsolescencia.get("resumen_ejecutivo", {}).get("total_articulos_obsoletos", 0),
                "valor_stock_obsoleto": obsolescencia.get("resumen_ejecutivo", {}).get("valor_stock_obsoleto", 0),
                "impacto_ambiental": "Bajo" if obsolescencia.get("resumen_ejecutivo", {}).get("articulos_criticos", 0) == 0 else
                                   "Medio" if obsolescencia.get("resumen_ejecutivo", {}).get("articulos_criticos", 0) <= 5 else
                                   "Alto"
            }
        }
        
        # Alertas ejecutivas
        alertas_ejecutivas = []
        
        if auditoria.get("resumen_ejecutivo", {}).get("puntuacion_calidad", 0) < 85:
            alertas_ejecutivas.append({
                "tipo": "Cumplimiento ISO",
                "mensaje": "La puntuación de calidad está por debajo del estándar ISO 9001",
                "prioridad": "Alta",
                "accion_requerida": "Revisión inmediata de procesos"
            })
        
        if calidad.get("metricas_globales", {}).get("tasa_errores", 0) > 5:
            alertas_ejecutivas.append({
                "tipo": "Control de Calidad",
                "mensaje": f"Tasa de errores ({calidad.get('metricas_globales', {}).get('tasa_errores', 0):.1f}%) supera el límite aceptable",
                "prioridad": "Media",
                "accion_requerida": "Capacitación del personal"
            })
        
        if obsolescencia.get("resumen_ejecutivo", {}).get("articulos_criticos", 0) > 0:
            alertas_ejecutivas.append({
                "tipo": "Gestión Ambiental",
                "mensaje": f"{obsolescencia.get('resumen_ejecutivo', {}).get('articulos_criticos', 0)} artículos en estado crítico de obsolescencia",
                "prioridad": "Media",
                "accion_requerida": "Plan de disposición responsable"
            })
        
        return {
            "metadatos": {
                "fecha_generacion": datetime.now().isoformat(),
                "tipo": "Dashboard ISO Ejecutivo",
                "normas_aplicadas": ["ISO 9001:2015", "ISO 14001:2015"]
            },
            "kpis_principales": kpis,
            "alertas_ejecutivas": alertas_ejecutivas,
            "resumen_cumplimiento": {
                "iso_9001": kpis["cumplimiento_iso_9001"]["puntuacion"] >= 85,
                "iso_14001": kpis["gestion_ambiental"]["impacto_ambiental"] in ["Bajo", "Medio"],
                "nivel_general": "Cumple" if (kpis["cumplimiento_iso_9001"]["puntuacion"] >= 85 and 
                                            kpis["gestion_ambiental"]["impacto_ambiental"] != "Alto") else "No cumple"
            },
            "proximas_acciones": [
                {
                    "accion": "Auditoría interna programada",
                    "fecha": (datetime.now() + timedelta(days=30)).isoformat(),
                    "responsable": "Departamento de Calidad"
                },
                {
                    "accion": "Revisión de obsolescencias",
                    "fecha": (datetime.now() + timedelta(days=15)).isoformat(),
                    "responsable": "Gestión de Inventarios"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generando dashboard ISO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando dashboard ISO: {str(e)}"
        )

@router.get("/global", response_model=Dict[str, Any])
async def get_stock_global_optimizado(
    pagina: int = Query(1, ge=1, description="Página actual (empezando en 1)"),
    limite: int = Query(100, ge=10, le=500, description="Número de artículos por página (10-500)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el stock global optimizado para todos los artículos en todos los depósitos.

    Args:
        pagina: Número de página para paginación
        limite: Número de artículos por página
        db: Sesión de base de datos

    Returns:
        Diccionario con información de artículos y paginación
    """
    try:
        # Obtener todos los artículos con stock positivo usando el servicio
        articulos = get_articulos_con_stock_positivo(db, limite=limite, offset=(pagina - 1) * limite)

        # Contar el total de artículos con stock positivo
        total_articulos = contar_articulos_con_stock_positivo(db)

        # Construir respuesta con paginación
        response = {
            "pagina": pagina,
            "limite": limite,
            "total": total_articulos,
            "articulos": articulos
        }

        return response
    except Exception as e:
        logger.error(f"Error al obtener stock global optimizado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener stock global: {str(e)}"
        )

@router.get("/global/resumen", response_model=Dict[str, Any])
async def get_resumen_ejecutivo_stock(db: Session = Depends(get_db)):
    """
    Obtiene un resumen ejecutivo del stock global para vista rápida de gerencia.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Resumen ejecutivo con KPIs principales
    """
    try:
        # Obtener resumen global
        resumen = get_resumen_stock_global(db)
        
        # Obtener top artículos por stock
        top_articulos = get_top_articulos_por_stock(db, 20)
        
        # Calcular indicadores adicionales
        indicadores_performance = {
            "eficiencia_ocupacion": resumen["porcentaje_ocupacion"],
            "nivel_diversificacion": len(top_articulos),
            "concentracion_stock": (top_articulos[0]["stock_total"] / resumen["stock_total"] * 100) if top_articulos and resumen["stock_total"] > 0 else 0,
            "promedio_stock_deposito": resumen["stock_total"] / resumen["total_depositos"] if resumen["total_depositos"] > 0 else 0
        }
        
        # Determinar alertas
        alertas = []
        if resumen["porcentaje_ocupacion"] < 50:
            alertas.append({
                "tipo": "Baja ocupación",
                "mensaje": f"Solo {resumen['porcentaje_ocupacion']:.1f}% de ubicaciones tienen stock",
                "severidad": "media"
            })
        
        if indicadores_performance["concentracion_stock"] > 30:
            alertas.append({
                "tipo": "Alta concentración",
                "mensaje": f"El {indicadores_performance['concentracion_stock']:.1f}% del stock está en un solo artículo",
                "severidad": "alta"
            })
        
        # Construir respuesta
        result = {
            "metadatos": {
                "fecha_generacion": datetime.now().isoformat(),
                "tipo": "Resumen Ejecutivo Stock",
                "version": "1.0"
            },
            "kpis_principales": {
                "total_articulos": resumen["total_articulos"],
                "total_depositos": resumen["total_depositos"],
                "valor_stock_total": resumen["stock_total"],
                "porcentaje_ocupacion": resumen["porcentaje_ocupacion"],
                "ubicaciones_activas": resumen["ubicaciones_con_stock"]
            },
            "indicadores_performance": indicadores_performance,
            "top_articulos": top_articulos[:10],  # Solo los top 10 para el resumen
            "alertas": alertas,
            "recomendaciones": [
                "Monitorear artículos con alta concentración de stock",
                "Optimizar ubicaciones con baja ocupación",
                "Revisar políticas de stock mínimo y máximo"
            ]
        }
        
        return result
    except Exception as e:
        logger.error(f"Error al obtener resumen ejecutivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen ejecutivo: {str(e)}"
        )

@router.get("/global/top-stock", response_model=List[Dict[str, Any]])
async def get_top_articulos_stock(
    limite: int = Query(50, ge=10, le=200, description="Número de artículos top a mostrar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los artículos con mayor stock consolidado de manera optimizada.
    
    Args:
        limite: Número de artículos top a mostrar
        db: Sesión de base de datos
        
    Returns:
        Lista de artículos con mayor stock
    """
    try:
        # Obtener top artículos
        top_articulos = get_top_articulos_por_stock(db, limite)
        
        # Agregar información adicional de análisis
        for articulo in top_articulos:
            # Calcular porcentaje del stock total
            articulo["porcentaje_stock_global"] = 0  # Se calculará después
            
            # Clasificación ABC simplificada
            if articulo["stock_total"] > 1000:
                articulo["categoria_abc"] = "A"
                articulo["prioridad"] = "Alta"
            elif articulo["stock_total"] > 100:
                articulo["categoria_abc"] = "B"
                articulo["prioridad"] = "Media"
            else:
                articulo["categoria_abc"] = "C"
                articulo["prioridad"] = "Baja"
        
        # Calcular porcentajes relativos
        total_stock = sum(art["stock_total"] for art in top_articulos)
        for articulo in top_articulos:
            articulo["porcentaje_stock_relativo"] = round(
                (articulo["stock_total"] / total_stock * 100), 2
            ) if total_stock > 0 else 0
        
        return top_articulos
    except Exception as e:
        logger.error(f"Error al obtener top artículos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener top artículos: {str(e)}"
        )

@router.get("/buscar", response_model=Dict[str, Any])
async def buscar_articulos_stock(
    termino: str = Query(..., min_length=3, description="Término de búsqueda (mínimo 3 caracteres)"),
    limite: int = Query(50, ge=10, le=100, description="Número máximo de resultados"),
    db: Session = Depends(get_db)
):
    """
    Busca artículos por nombre/descripción que tengan stock positivo.
    
    Args:
        termino: Término de búsqueda
        limite: Número máximo de resultados
        db: Sesión de base de datos
        
    Returns:
        Resultados de búsqueda con stock
    """
    try:
        # Preparar término de búsqueda
        termino_busqueda = f"%{termino.lower()}%"
          # Ejecutar búsqueda optimizada
        query = text("""
            SELECT TOP (:limite) DISTINCT 
                s.codigo_art,
                s.id_deposito,
                a.descripcion as articulo_descripcion,
                d.descripcion as deposito_descripcion,
                s.cant_disponible as stock_fisico,
                s.cant_reservado as stock_reservado,
                s.cant_preparado as stock_preparado
            FROM stock s
            INNER JOIN articulos a ON s.codigo_art = a.id
            INNER JOIN depositos d ON s.id_deposito = d.id
            WHERE s.cant_disponible > 0 
            AND LOWER(a.descripcion) LIKE :termino
            ORDER BY s.cant_disponible DESC, a.descripcion
        """)
        
        resultados = db.execute(query, {
            "termino": termino_busqueda,
            "limite": limite
        }).fetchall()
        
        # Procesar resultados
        articulos_encontrados = []
        for row in resultados:
            disponible = float(row.stock_fisico or 0) - float(row.stock_reservado or 0) - float(row.stock_preparado or 0)
            
            articulos_encontrados.append({
                "codigo_art": row.codigo_art,
                "id_deposito": row.id_deposito,
                "articulo_descripcion": row.articulo_descripcion or f"Artículo {row.codigo_art}",
                "deposito_descripcion": row.deposito_descripcion or f"Depósito {row.id_deposito}",
                "stock_fisico": float(row.stock_fisico) if row.stock_fisico else 0.0,
                "stock_reservado": float(row.stock_reservado) if row.stock_reservado else 0.0,
                "stock_preparado": float(row.stock_preparado) if row.stock_preparado else 0.0,
                "stock_disponible": disponible,
                "relevancia": "alta" if termino.lower() in row.articulo_descripcion.lower()[:50] else "media"
            })
        
        return {
            "metadatos": {
                "termino_busqueda": termino,
                "fecha_busqueda": datetime.now().isoformat(),
                "total_encontrados": len(articulos_encontrados)
            },
            "resultados": articulos_encontrados,
            "sugerencias": {
                "refinar_busqueda": len(articulos_encontrados) > limite * 0.8,
                "ampliar_busqueda": len(articulos_encontrados) < 5,
                "termino_muy_especifico": len(articulos_encontrados) == 0
            }
        }
    except Exception as e:
        logger.error(f"Error en búsqueda de artículos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )


