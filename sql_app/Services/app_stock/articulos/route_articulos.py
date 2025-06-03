from fastapi import APIRouter, HTTPException, status, Depends, Query, Body, Request
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_articulos import ArticulosCreate, ArticulosUpdate, ArticulosRead
from .model_articulos import Articulos as ArticulosModel
from .service_articulos import (
    create_articulos, get_articulos, get_articulos_by_codigo, gets_articulos, delete_articulos, update_articulos,
    actualizar_precio_articulo, actualizar_precios_masivos, get_articulos_stats,
    get_historial_precios, generar_codigo_barra, generar_codigo_qr, get_recent_price_changes
)
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Services.security.security import get_current_user  # Importamos la función de seguridad
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="static")

router = APIRouter(
    prefix="/articulos",
    tags=["articulos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ArticulosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_articulos(articulos: ArticulosCreate, db: Session = Depends(get_db)):
    if articulos.codigo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo código es obligatorio")
    try:
        articulos_model = ArticulosModel(**articulos.model_dump())
        db_articulos = create_articulos(db=db, articulos=articulos_model)
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al crear Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=ArticulosRead)
async def routes_get_articulos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_articulos = get_articulos(db, id)
        if not db_articulos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos no encontrado")
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al obtener Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[ArticulosRead])
async def routes_gets_articulos_all(db: Session = Depends(get_db)):
    try:
        db_articulos = gets_articulos(db)
        if not db_articulos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: articuloss no encontrados")
        return [ArticulosRead.model_validate(articulos) for articulos in db_articulos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=ArticulosRead)
async def routes_delete_articulos_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_articulos = get_articulos(db, id)
        if not resultado_articulos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos no encontrado")
        db_articulos = delete_articulos(db, id)
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al eliminar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=ArticulosRead)
async def routes_update_articulos(
    id: int, 
    articulos: ArticulosUpdate, 
    usuario_id: Optional[int] = Query(None, description="ID del usuario que realiza el cambio"),
    motivo: Optional[str] = Query(None, description="Motivo del cambio de precio"),
    db: Session = Depends(get_db)
):
    logger.info(f"Actualizando Articulos con id = {id}")
    try:
        articulos_data = articulos.model_dump()
        db_articulos = update_articulos(
            db=db, 
            id=id, 
            articulos_data=articulos_data, 
            usuario_id=usuario_id, 
            motivo=motivo
        )
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al actualizar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"static/app_stock/articulos/articulos.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")


@router.patch("/{articulo_id}/precio/{tipo_precio}", response_model=ArticulosRead)
async def actualizar_precio(
    articulo_id: int,
    tipo_precio: str,
    nuevo_precio: float = Query(..., description="Nuevo precio"),
    usuario_id: Optional[int] = Query(None, description="ID del usuario que realiza el cambio"),
    motivo: Optional[str] = Query(None, description="Motivo del cambio de precio"),
    db: Session = Depends(get_db)
):
    """
    Actualiza el precio de un artículo (precio de costo o precio de venta)
    
    - **articulo_id**: ID del artículo a actualizar
    - **tipo_precio**: Tipo de precio a actualizar ('costo' o 'venta')
    - **nuevo_precio**: Nuevo precio a establecer
    - **usuario_id**: ID del usuario que realiza el cambio
    - **motivo**: Motivo del cambio de precio
    """
    if tipo_precio not in ['costo', 'venta']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de precio debe ser 'costo' o 'venta'"
        )
        
    try:
        articulo_actualizado = actualizar_precio_articulo(
            db=db,
            articulo_id=articulo_id,
            nuevo_precio=nuevo_precio,
            tipo_precio=tipo_precio,
            usuario_id=usuario_id,
            motivo=motivo
        )
        
        return ArticulosRead.model_validate(articulo_actualizado)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar precio del artículo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar precio: {str(e)}"
        )


@router.post("/actualizar-precios-masivo", response_model=Dict[str, Any])
async def actualizar_precios_masivo(
    porcentaje: float = Query(..., description="Porcentaje de variación de precios"),
    tipo_precio: str = Query(..., description="Tipo de precio a actualizar ('costo' o 'venta')"),
    filtro: Dict[str, Any] = Body({}, description="Filtros para seleccionar artículos (id_tipo, marca, modelo)"),
    usuario_id: Optional[int] = Query(None, description="ID del usuario que realiza el cambio"),
    motivo: Optional[str] = Query(None, description="Motivo del cambio de precios"),
    db: Session = Depends(get_db)
):
    """
    Actualiza masivamente los precios de artículos aplicando un porcentaje de variación
    
    - **porcentaje**: Porcentaje de variación (ej: 10 para subir 10%, -5 para bajar 5%)
    - **tipo_precio**: Tipo de precio a actualizar ('costo' o 'venta')
    - **filtro**: Filtros para seleccionar artículos (ejemplo: {"id_tipo": "1", "marca": "Samsung"})
    - **usuario_id**: ID del usuario que realiza el cambio
    - **motivo**: Motivo del cambio de precios
    """
    if tipo_precio not in ['costo', 'venta']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de precio debe ser 'costo' o 'venta'"
        )
        
    try:
        num_actualizados = actualizar_precios_masivos(
            db=db,
            filtro=filtro,
            porcentaje=porcentaje,
            tipo_precio=tipo_precio,
            usuario_id=usuario_id,
            motivo=motivo
        )
        
        return {
            "success": True,
            "message": f"Precios actualizados correctamente",
            "articulos_actualizados": num_actualizados,
            "porcentaje_aplicado": porcentaje,
            "tipo_precio": tipo_precio
        }
    except Exception as e:
        logger.error(f"Error en actualización masiva de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar precios: {str(e)}"
        )

@router.get("/dashboard", response_class=HTMLResponse)
async def get_articulos_dashboard(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Muestra el dashboard de análisis y gestión de artículos.
    """
    try:
        # Obtenemos estadísticas para el dashboard
        stats = get_articulos_stats(db)
        
        # Datos para el gráfico de precios (últimos 6 meses)
        fecha_inicio = datetime.now() - timedelta(days=180)
        historial = get_historial_precios(db, fecha_inicio=fecha_inicio)
        
        # Procesamos los datos para el formato que espera el gráfico
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        actual_month = datetime.now().month - 1  # 0-indexed para array
        
        # Procesamos datos para el gráfico como antes y creamos price_data
        # ... (código existente para price_data)
        
        # En lugar de cargar directamente el archivo HTML, usamos Jinja2 para pasar el contexto
        return templates.TemplateResponse(
            "app_stock/articulos/articulos_dashboard.html", 
            {
                "request": request,
                "user": current_user,  # Pasamos la información del usuario
                "articulos_count": stats.get("total_articulos", 0),
                "precio_cambios_count": stats.get("cambios_precio_30_dias", 0),
                "barcode_count": stats.get("total_codigos_barras", 0),
                "qr_count": stats.get("total_codigos_qr", 0)
                # Si necesitas pasar price_data, agrégalo aquí
            }
        )
    except Exception as e:
        logger.error(f"Error al obtener el dashboard de artículos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener el dashboard de artículos."
        )

@router.get("/estadisticas", response_model=Dict[str, Any])
async def get_estadisticas_articulos(db: Session = Depends(get_db)):
    """
    Obtiene las estadísticas de artículos para el dashboard
    
    Incluye:
    - Total de artículos
    - Número de cambios de precio en los últimos 30 días
    - Total de artículos con código de barras
    - Total de artículos con código QR
    """
    try:
        stats = get_articulos_stats(db)
        
        # Datos para el gráfico de precios (últimos 6 meses)
        fecha_inicio = datetime.now() - timedelta(days=180)
        historial = get_historial_precios(db, fecha_inicio=fecha_inicio)
        
        # Procesamos los datos para el formato que espera el gráfico
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        actual_month = datetime.now().month - 1  # 0-indexed para array
        
        # Meses para el gráfico (últimos 6)
        labels = []
        for i in range(5, -1, -1):
            month_idx = (actual_month - i) % 12
            labels.append(meses[month_idx])
        
        # Preparamos datos para el gráfico
        price_data = {
            "labels": labels,
            "costo": [0, 0, 0, 0, 0, 0],  # Cambios en precio de costo
            "venta": [0, 0, 0, 0, 0, 0]   # Cambios en precio de venta
        }
        
        # Procesamos el historial para llenar los arrays con datos reales
        if historial and len(historial) > 0:
            # Inicializamos contadores de cambios por mes y tipo
            cambios_por_mes_costo = {i: 0 for i in range(-5, 1)}  # -5, -4, -3, -2, -1, 0 (últimos 6 meses)
            cambios_por_mes_venta = {i: 0 for i in range(-5, 1)}  # -5, -4, -3, -2, -1, 0 (últimos 6 meses)
            
            # Fecha actual
            now = datetime.now()
            current_month = now.month
            current_year = now.year
            
            # Contamos los cambios por mes y tipo
            for cambio in historial:
                fecha_cambio = cambio.fecha_cambio if hasattr(cambio, 'fecha_cambio') else datetime.now()
                tipo_precio = cambio.tipo_precio if hasattr(cambio, 'tipo_precio') else "costo"
                
                # Calculamos la diferencia de meses con respecto al mes actual
                month_diff = (current_year - fecha_cambio.year) * 12 + (current_month - fecha_cambio.month)
                
                # Solo consideramos los últimos 6 meses (-5 a 0)
                if 0 <= month_diff < 6:
                    idx = -month_diff  # Convertimos a índice negativo (0 = mes actual, -5 = hace 5 meses)
                    if tipo_precio == "costo":
                        cambios_por_mes_costo[idx] += 1
                    elif tipo_precio == "venta":
                        cambios_por_mes_venta[idx] += 1
            
            # Llenamos los arrays con los datos calculados
            for i in range(6):
                # El índice en el array es inverso al mes (0 es el más antiguo, 5 el más reciente)
                # Mientras que en cambios_por_mes, -5 es el más antiguo y 0 el más reciente
                idx = i - 5  # Convertimos i (0-5) a índice (-5-0)
                price_data["costo"][i] = cambios_por_mes_costo.get(idx, 0)
                price_data["venta"][i] = cambios_por_mes_venta.get(idx, 0)
        
        return {
            "articulos_count": stats.get("total_articulos", 0),
            "precio_cambios_count": stats.get("cambios_precio_30_dias", 0),
            "barcode_count": stats.get("total_codigos_barras", 0),
            "qr_count": stats.get("total_codigos_qr", 0),
            "price_data": price_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de artículos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

# Se eliminó la ruta /historial-precios que ahora está en route_historial_precios.py

# Método para obtener un artículo por código
@router.get("/codigo/{codigo}")
def get_articulo_by_codigo(codigo: str, db: Session = Depends(get_db)):
    articulo = get_articulos_by_codigo(db, codigo)
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return articulo

@router.get("/codigos-barras", response_class=HTMLResponse)
async def get_codigos_barras_pagina():
    """
    Muestra la página de gestión de códigos de barras.
    """
    try:
        # Esta página aún no existe, redireccionamos temporalmente al dashboard
        with open("static/app_stock/articulos/articulos_dashboard.html", "r", encoding="utf-8") as file:
            html_content = file.read()
            
        # En el futuro, aquí iría la página específica de códigos de barras
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de códigos de barras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener la página de códigos de barras."
        )

@router.get("/codigos-qr", response_class=HTMLResponse)
async def get_codigos_qr_pagina():
    """
    Muestra la página de gestión de códigos QR.
    """
    try:
        # Esta página aún no existe, redireccionamos temporalmente al dashboard
        with open("static/app_stock/articulos/articulos_dashboard.html", "r", encoding="utf-8") as file:
            html_content = file.read()
            
        # En el futuro, aquí iría la página específica de códigos QR
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de códigos QR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener la página de códigos QR."
        )

@router.get("/etiquetas", response_class=HTMLResponse)
async def get_etiquetas_pagina():
    """
    Muestra la página de gestión de etiquetas completas.
    """
    try:
        # Esta página aún no existe, redireccionamos temporalmente al dashboard
        with open("static/app_stock/articulos/articulos_dashboard.html", "r", encoding="utf-8") as file:
            html_content = file.read()
            
        # En el futuro, aquí iría la página específica de etiquetas
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la página de etiquetas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener la página de etiquetas."
        )

@router.post("/generar-barcode/{articulo_id}", response_model=Dict[str, Any])
async def generar_barcode(
    articulo_id: int,
    tipo: str = Query("CODE128", description="Tipo de código de barras (CODE128, EAN13, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Genera un código de barras para un artículo
    
    - **articulo_id**: ID del artículo
    - **tipo**: Tipo de código de barras (CODE128, EAN13, etc.)
    """
    try:
        resultado = generar_codigo_barra(db, articulo_id, tipo)
        
        return {
            "success": True,
            "message": "Código de barras generado correctamente",
            "barcode_url": resultado.get("url", ""),
            "articulo_id": articulo_id,
            "codigo": resultado.get("codigo", "")
        }
    except Exception as e:
        logger.error(f"Error al generar código de barras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código de barras: {str(e)}"
        )

@router.post("/generar-qr/{articulo_id}", response_model=Dict[str, Any])
async def generar_qr(
    articulo_id: int,
    incluir_precio: bool = Query(True, description="Incluir precio en el QR"),
    db: Session = Depends(get_db)
):
    """
    Genera un código QR para un artículo
    
    - **articulo_id**: ID del artículo
    - **incluir_precio**: Si se debe incluir el precio en el QR
    """
    try:
        resultado = generar_codigo_qr(db, articulo_id, incluir_precio)
        
        return {
            "success": True,
            "message": "Código QR generado correctamente",
            "qr_url": resultado.get("url", ""),
            "articulo_id": articulo_id,
            "datos": resultado.get("datos", "")
        }
    except Exception as e:
        logger.error(f"Error al generar código QR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código QR: {str(e)}"
        )

@router.get("/actividades-recientes", response_model=List[Dict[str, Any]])
async def get_actividades_recientes(
    limit: int = Query(5, description="Número máximo de actividades a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene las actividades recientes relacionadas con artículos (cambios de precio, generación de códigos, etc.)
    
    - **limit**: Número máximo de actividades a retornar
    """
    try:
        # Por ahora solo retornamos cambios de precio recientes
        cambios = get_recent_price_changes(db, limit)
        
        return cambios
    except Exception as e:
        logger.error(f"Error al obtener actividades recientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener actividades recientes: {str(e)}"
        )