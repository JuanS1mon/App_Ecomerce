# Imports de bibliotecas estándar
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging
import os

# Imports de terceros
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.db.database import get_db
from sql_app.Services.app_stock.articulos.schema_articulos import CodigoBarrasRequest, QRCodeRequest
from sql_app.Services.app_stock.articulos.service_codigos import (
    generar_codigo_barras, 
    generar_codigo_qr, 
    generar_etiqueta_completa
)

router = APIRouter(
    prefix="/articulos",
    tags=["codigos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

logger = logging.getLogger(__name__)

@router.post("/{articulo_id}/codigo-barras", response_model=Dict[str, Any])
async def crear_codigo_barras(
    articulo_id: int,
    request: CodigoBarrasRequest,
    db: Session = Depends(get_db)
):
    """
    Genera un código de barras para un artículo
    
    - **articulo_id**: ID del artículo
    - **tipo**: Tipo de código de barras ('ean13', 'ean8', 'code128', 'upca')
    - **valor**: Valor opcional para el código (si se omite, se generará automáticamente)
    - **guardar_en_db**: Si se debe guardar el código en la base de datos
    """
    try:
        resultado = generar_codigo_barras(
            db=db,
            articulo_id=articulo_id,
            tipo_codigo=request.tipo,
            valor_codigo=request.valor,
            guardar_en_db=request.guardar_en_db
        )
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar código de barras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código de barras: {str(e)}"
        )

@router.post("/{articulo_id}/qr", response_model=Dict[str, Any])
async def crear_codigo_qr(
    articulo_id: int,
    request: QRCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Genera un código QR para un artículo
    
    - **articulo_id**: ID del artículo
    - **datos**: Datos a codificar en el QR
    - **version**: Versión del QR (1-40)
    - **box_size**: Tamaño de cada caja del QR
    - **border**: Borde del QR
    - **guardar_en_db**: Si se debe guardar el código en la base de datos
    """
    try:
        resultado = generar_codigo_qr(
            db=db,
            articulo_id=articulo_id,
            datos=request.datos,
            version=request.version,
            box_size=request.box_size,
            border=request.border,
            guardar_en_db=request.guardar_en_db
        )
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar código QR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código QR: {str(e)}"
        )

@router.post("/{articulo_id}/etiqueta", response_model=Dict[str, Any])
async def crear_etiqueta_completa(
    articulo_id: int,
    incluir_codigo_barras: bool = Query(True, description="Incluir código de barras en la etiqueta"),
    incluir_qr: bool = Query(True, description="Incluir QR en la etiqueta"),
    formato_cb: str = Query("ean13", description="Formato del código de barras"),
    datos_adicionales: Dict[str, Any] = Body({}, description="Datos adicionales para incluir en el QR"),
    db: Session = Depends(get_db)
):
    """
    Genera una etiqueta completa con código de barras y/o QR para un artículo
    
    - **articulo_id**: ID del artículo
    - **incluir_codigo_barras**: Si se debe incluir código de barras
    - **incluir_qr**: Si se debe incluir código QR
    - **formato_cb**: Formato del código de barras
    - **datos_adicionales**: Datos adicionales para incluir en el QR
    """
    try:
        resultado = generar_etiqueta_completa(
            db=db,
            articulo_id=articulo_id,
            incluir_codigo_barras=incluir_codigo_barras,
            incluir_qr=incluir_qr,
            formato_cb=formato_cb,
            datos_adicionales=datos_adicionales
        )
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar etiqueta completa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar etiqueta completa: {str(e)}"
        )

@router.get("/{articulo_id}/imprimir-etiqueta", response_model=Dict[str, Any])
async def preparar_impresion_etiqueta(
    articulo_id: int,
    incluir_precio: bool = Query(True, description="Incluir precio en la etiqueta"),
    incluir_codigo_barras: bool = Query(True, description="Incluir código de barras en la etiqueta"),
    incluir_qr: bool = Query(True, description="Incluir QR en la etiqueta"),
    formato_cb: str = Query("ean13", description="Formato del código de barras"),
    db: Session = Depends(get_db)
):
    """
    Prepara los datos para imprimir una etiqueta para un artículo
    
    - **articulo_id**: ID del artículo
    - **incluir_precio**: Si se debe incluir el precio en la etiqueta
    - **incluir_codigo_barras**: Si se debe incluir código de barras
    - **incluir_qr**: Si se debe incluir código QR
    - **formato_cb**: Formato del código de barras
    """
    try:
        # Datos adicionales para el QR basados en configuración
        datos_adicionales = {
            "incluir_precio": incluir_precio
        }
        
        # Generar la etiqueta completa
        resultado = generar_etiqueta_completa(
            db=db,
            articulo_id=articulo_id,
            incluir_codigo_barras=incluir_codigo_barras,
            incluir_qr=incluir_qr,
            formato_cb=formato_cb,
            datos_adicionales=datos_adicionales
        )
        
        # Añadir datos específicos para la impresión
        resultado["listo_para_imprimir"] = True
        resultado["incluir_precio"] = incluir_precio
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al preparar impresión de etiqueta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al preparar impresión de etiqueta: {str(e)}"
        )

@router.get("/imprimir-etiquetas-multiple", response_model=List[Dict[str, Any]])
async def preparar_impresion_etiquetas_multiple(
    articulo_ids: str = Query(..., description="IDs de artículos separados por comas"),
    incluir_precio: bool = Query(True, description="Incluir precio en las etiquetas"),
    incluir_codigo_barras: bool = Query(True, description="Incluir código de barras en las etiquetas"),
    incluir_qr: bool = Query(True, description="Incluir QR en las etiquetas"),
    formato_cb: str = Query("ean13", description="Formato del código de barras"),
    db: Session = Depends(get_db)
):
    """
    Prepara los datos para imprimir etiquetas de múltiples artículos
    
    - **articulo_ids**: IDs de artículos separados por comas (ejemplo: "1,2,3")
    - **incluir_precio**: Si se debe incluir el precio en las etiquetas
    - **incluir_codigo_barras**: Si se debe incluir código de barras
    - **incluir_qr**: Si se debe incluir QR
    - **formato_cb**: Formato del código de barras
    """
    try:
        # Convertir la cadena de IDs en una lista de enteros
        try:
            ids_lista = [int(id.strip()) for id in articulo_ids.split(',') if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los IDs de artículos deben ser números enteros separados por comas"
            )
            
        if not ids_lista:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron IDs de artículos válidos"
            )
            
        # Generar etiquetas para cada artículo
        resultados = []
        for articulo_id in ids_lista:
            try:
                datos_adicionales = {
                    "incluir_precio": incluir_precio
                }
                
                resultado = generar_etiqueta_completa(
                    db=db,
                    articulo_id=articulo_id,
                    incluir_codigo_barras=incluir_codigo_barras,
                    incluir_qr=incluir_qr,
                    formato_cb=formato_cb,
                    datos_adicionales=datos_adicionales
                )
                
                resultado["listo_para_imprimir"] = True
                resultado["incluir_precio"] = incluir_precio
                resultados.append(resultado)
            except HTTPException as e:
                # Registrar el error pero continuar con el siguiente artículo
                logger.warning(f"No se pudo generar etiqueta para artículo ID {articulo_id}: {e.detail}")
                resultados.append({
                    "articulo_id": articulo_id,
                    "error": e.detail,
                    "listo_para_imprimir": False
                })
        
        return resultados
    except Exception as e:
        logger.error(f"Error al preparar impresión de etiquetas múltiples: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al preparar impresión de etiquetas múltiples: {str(e)}"
        )