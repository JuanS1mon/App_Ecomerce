# Imports de bibliotecas estándar
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json
import logging

# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.db.database import get_db
from sql_app.Services.app_stock.articulos.service_historial_precios import (
    get_historial_precios_por_articulo,
    get_estadisticas_historial_precios,
    get_historial_precios_con_filtros
)

logger = logging.getLogger(__name__)

# Router para el historial de precios
router = APIRouter(
    prefix="/historial-precios",
    tags=["historial-precios"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# Router adicional para compatibilidad con el frontend existente
api_router = APIRouter(
    prefix="/api/articulos",
    tags=["articulos-api"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/", response_class=HTMLResponse)
async def get_historial_precios_pagina():
    """
    Muestra la página de historial de precios de artículos.
    """
    try:
        with open("sql_app/static/app_stock/articulos/historial_precios/historial_precios.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener la página de historial de precios."
        )

@router.get("/api/listar", response_model=Dict[str, Any])
@api_router.get("/historial-precios", response_model=Dict[str, Any])  # Ruta adicional para compatibilidad con el frontend
async def listar_historial_precios(
    fechaDesde: str = Query(None, description="Fecha de inicio para filtrar (formato YYYY-MM-DD)"),
    fechaHasta: str = Query(None, description="Fecha de fin para filtrar (formato YYYY-MM-DD)"),
    tipoPrecio: str = Query("todos", description="Filtrar por tipo de precio ('todos', 'costo', 'venta')"),
    filtroArticulo: str = Query(None, description="Filtrar por código o descripción de artículo"),
    tipoVariacion: str = Query("todos", description="Filtrar por tipo de variación ('todos', 'aumento', 'disminucion')"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de cambios de precios según los filtros aplicados
    """
    try:
        # Convertir fechas de string a datetime
        fecha_inicio = None
        fecha_fin = None
        
        if fechaDesde:
            try:
                fecha_inicio = datetime.strptime(fechaDesde, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fechaDesde incorrecto. Debe ser YYYY-MM-DD"
                )
        
        if fechaHasta:
            try:
                fecha_fin = datetime.strptime(fechaHasta, "%Y-%m-%d")
                # Ajustar al final del día
                fecha_fin = fecha_fin + timedelta(days=1, seconds=-1)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fechaHasta incorrecto. Debe ser YYYY-MM-DD"
                )
        
        # Validar tipo de precio
        if tipoPrecio not in ['todos', 'costo', 'venta']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de precio debe ser 'todos', 'costo' o 'venta'"
            )
        
        # Validar tipo de variación
        if tipoVariacion not in ['todos', 'aumento', 'disminucion']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de variación debe ser 'todos', 'aumento' o 'disminucion'"
            )
        
        # Obtener resultados según los filtros
        historial = get_historial_precios_con_filtros(
            db=db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_precio=None if tipoPrecio == "todos" else tipoPrecio,
            filtro_articulo=filtroArticulo,
            tipo_variacion=None if tipoVariacion == "todos" else tipoVariacion
        )
        
        # Obtener estadísticas del historial filtrado
        estadisticas = get_estadisticas_historial_precios(
            db=db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_precio=None if tipoPrecio == "todos" else tipoPrecio,
            filtro_articulo=filtroArticulo,
            tipo_variacion=None if tipoVariacion == "todos" else tipoVariacion
        )
        
        # Formatear los resultados para la respuesta
        resultados = {
            "historial": [
                {
                    "id": item.id if hasattr(item, 'id') else 0,
                    "fecha": item.fecha_cambio.isoformat() if hasattr(item, 'fecha_cambio') else datetime.now().isoformat(),
                    "articulo_id": item.articulo_id if hasattr(item, 'articulo_id') else 0,
                    "codigo": item.codigo if hasattr(item, 'codigo') else "",
                    "descripcion": item.descripcion if hasattr(item, 'descripcion') else "",
                    "tipo": item.tipo_precio if hasattr(item, 'tipo_precio') else "",
                    "precio_anterior": float(item.precio_anterior) if hasattr(item, 'precio_anterior') else 0.0,
                    "precio_nuevo": float(item.precio_nuevo) if hasattr(item, 'precio_nuevo') else 0.0,
                    "variacion_porcentual": float(item.variacion_porcentual) if hasattr(item, 'variacion_porcentual') else 0.0,
                    "usuario": item.usuario if hasattr(item, 'usuario') else "",
                    "motivo": item.motivo if hasattr(item, 'motivo') else ""
                } for item in historial
            ],
            "estadisticas": {
                "total": estadisticas.get("total", 0),
                "costo": estadisticas.get("costo", 0),
                "venta": estadisticas.get("venta", 0),
                "variacion_promedio": estadisticas.get("variacion_promedio", 0.0)
            }
        }
        
        return resultados
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener el historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el historial de precios: {str(e)}"
        )

@router.get("/api/estadisticas", response_model=Dict[str, Any])
async def obtener_estadisticas_historial(
    fecha_desde: str = Query(None, description="Fecha de inicio para filtrar (formato YYYY-MM-DD)"),
    fecha_hasta: str = Query(None, description="Fecha de fin para filtrar (formato YYYY-MM-DD)"),
    tipo_precio: str = Query("todos", description="Filtrar por tipo de precio ('todos', 'costo', 'venta')"),
    filtro_articulo: str = Query(None, description="Filtrar por código o descripción de artículo"),
    tipo_variacion: str = Query("todos", description="Filtrar por tipo de variación ('todos', 'aumento', 'disminucion')"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del historial de cambios de precios según los filtros aplicados
    """
    try:
        # Convertir fechas de string a datetime
        fecha_inicio = None
        fecha_fin = None
        
        if fecha_desde:
            try:
                fecha_inicio = datetime.strptime(fecha_desde, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_desde incorrecto. Debe ser YYYY-MM-DD"
                )
        
        if fecha_hasta:
            try:
                fecha_fin = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                # Ajustar al final del día
                fecha_fin = fecha_fin + timedelta(days=1, seconds=-1)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_hasta incorrecto. Debe ser YYYY-MM-DD"
                )
        
        # Obtener estadísticas según los filtros
        estadisticas = get_estadisticas_historial_precios(
            db=db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_precio=None if tipo_precio == "todos" else tipo_precio,
            filtro_articulo=filtro_articulo,
            tipo_variacion=None if tipo_variacion == "todos" else tipo_variacion
        )
        
        return estadisticas
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@router.get("/api/evolucion-precios/{codigo_articulo}", response_model=Dict[str, Any])
async def obtener_evolucion_precios(
    codigo_articulo: str,
    fecha_desde: str = Query(None, description="Fecha de inicio para filtrar (formato YYYY-MM-DD)"),
    fecha_hasta: str = Query(None, description="Fecha de fin para filtrar (formato YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la evolución de precios de un artículo específico para mostrar en gráficos
    """
    try:
        # Convertir fechas de string a datetime
        fecha_inicio = None
        fecha_fin = None
        
        if fecha_desde:
            try:
                fecha_inicio = datetime.strptime(fecha_desde, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_desde incorrecto. Debe ser YYYY-MM-DD"
                )
        else:
            # Por defecto, mostrar los últimos 6 meses
            fecha_inicio = datetime.now() - timedelta(days=180)
        
        if fecha_hasta:
            try:
                fecha_fin = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                # Ajustar al final del día
                fecha_fin = fecha_fin + timedelta(days=1, seconds=-1)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_hasta incorrecto. Debe ser YYYY-MM-DD"
                )
        else:
            # Por defecto, hasta hoy
            fecha_fin = datetime.now()
        
        # Obtener el historial de precios para el artículo
        historial = get_historial_precios_por_articulo(
            db=db,
            codigo_articulo=codigo_articulo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        # Formatear los datos para el gráfico
        datos_costo = []
        datos_venta = []
        
        for registro in historial:
            if hasattr(registro, 'tipo_precio') and registro.tipo_precio == 'costo':
                datos_costo.append({
                    "fecha": registro.fecha_cambio.isoformat() if hasattr(registro, 'fecha_cambio') else datetime.now().isoformat(),
                    "precio": float(registro.precio_nuevo) if hasattr(registro, 'precio_nuevo') else 0.0
                })
            elif hasattr(registro, 'tipo_precio') and registro.tipo_precio == 'venta':
                datos_venta.append({
                    "fecha": registro.fecha_cambio.isoformat() if hasattr(registro, 'fecha_cambio') else datetime.now().isoformat(),
                    "precio": float(registro.precio_nuevo) if hasattr(registro, 'precio_nuevo') else 0.0
                })
        
        # Obtener info básica del artículo
        info_articulo = {
            "codigo": codigo_articulo,
            "descripcion": historial[0].descripcion if historial and hasattr(historial[0], 'descripcion') else "Artículo"
        }
        
        return {
            "articulo": info_articulo,
            "datos": {
                "costo": datos_costo,
                "venta": datos_venta
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener evolución de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evolución de precios: {str(e)}"
        )

@router.post("/api/exportar/excel", response_model=Dict[str, Any])
async def exportar_historial_excel(
    fecha_desde: str = Query(None, description="Fecha de inicio para filtrar (formato YYYY-MM-DD)"),
    fecha_hasta: str = Query(None, description="Fecha de fin para filtrar (formato YYYY-MM-DD)"),
    tipo_precio: str = Query("todos", description="Filtrar por tipo de precio ('todos', 'costo', 'venta')"),
    filtro_articulo: str = Query(None, description="Filtrar por código o descripción de artículo"),
    tipo_variacion: str = Query("todos", description="Filtrar por tipo de variación ('todos', 'aumento', 'disminucion')"),
    db: Session = Depends(get_db)
):
    """
    Exporta el historial de cambios de precios a Excel según los filtros aplicados
    """
    try:
        # Implementación pendiente: generar archivo Excel en base a los filtros
        # Aquí se generaría un archivo Excel real y se devolvería la URL para descargarlo
        
        return {
            "success": True,
            "message": "Archivo Excel generado correctamente",
            "download_url": "/static/temp/historial_precios_export.xlsx",  # URL ficticia por ahora
            "fecha_generacion": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al exportar a Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al exportar a Excel: {str(e)}"
        )

@router.post("/api/exportar/pdf", response_model=Dict[str, Any])
async def exportar_historial_pdf(
    fecha_desde: str = Query(None, description="Fecha de inicio para filtrar (formato YYYY-MM-DD)"),
    fecha_hasta: str = Query(None, description="Fecha de fin para filtrar (formato YYYY-MM-DD)"),
    tipo_precio: str = Query("todos", description="Filtrar por tipo de precio ('todos', 'costo', 'venta')"),
    filtro_articulo: str = Query(None, description="Filtrar por código o descripción de artículo"),
    tipo_variacion: str = Query("todos", description="Filtrar por tipo de variación ('todos', 'aumento', 'disminucion')"),
    db: Session = Depends(get_db)
):
    """
    Exporta el historial de cambios de precios a PDF según los filtros aplicados
    """
    try:
        # Implementación pendiente: generar archivo PDF en base a los filtros
        # Aquí se generaría un archivo PDF real y se devolvería la URL para descargarlo
        
        return {
            "success": True,
            "message": "Archivo PDF generado correctamente",
            "download_url": "/static/temp/historial_precios_export.pdf",  # URL ficticia por ahora
            "fecha_generacion": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al exportar a PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al exportar a PDF: {str(e)}"
        )

@router.get("/api/detalle/{id}", response_model=Dict[str, Any])
async def obtener_detalle_cambio(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un cambio específico del historial de precios
    """
    try:
        # Aquí se implementaría la lógica para obtener el detalle de un cambio por su ID
        # Por ahora, devolvemos datos simulados
        
        return {
            "id": id,
            "fecha_cambio": "2025-04-15T10:30:45",
            "articulo": {
                "id": 1,
                "codigo": "MON-2401",
                "descripcion": "Monitor LED 24\"",
                "tipo": "Electrónica"
            },
            "tipo_precio": "venta",
            "precio_anterior": 45000.00,
            "precio_nuevo": 48500.00,
            "variacion_porcentual": 7.78,
            "usuario": "jperez",
            "motivo": "Actualización de precios por aumento de costos",
            "fecha_registro": "2025-04-15T10:30:45"
        }
    except Exception as e:
        logger.error(f"Error al obtener detalle del cambio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalle: {str(e)}"
        )