from sqlalchemy.orm import Session
import os
import json
import uuid
import barcode
from barcode.writer import ImageWriter
import qrcode
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging
from datetime import datetime

from .model_articulos import Articulos
from .service_articulos import get_articulos, update_articulos

logger = logging.getLogger(__name__)

# Configuración de rutas para almacenamiento de imágenes
BASE_DIR = Path("sql_app/static/images/codigos")
BARCODE_DIR = BASE_DIR / "barcode"
QR_DIR = BASE_DIR / "qr"

# Crear directorios si no existen
os.makedirs(BARCODE_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

# Formatos de códigos de barras soportados
BARCODE_FORMATS = {
    'ean13': barcode.EAN13,
    'ean8': barcode.EAN8,
    'code128': barcode.Code128,
    'upca': barcode.UPCA
}


def generar_codigo_barras(
    db: Session, 
    articulo_id: int, 
    tipo_codigo: str, 
    valor_codigo: Optional[str] = None,
    guardar_en_db: bool = True
) -> Dict[str, Any]:
    """
    Genera un código de barras para un artículo
    
    Args:
        db: Sesión de base de datos
        articulo_id: ID del artículo
        tipo_codigo: Tipo de código de barras (ean13, ean8, code128, upca)
        valor_codigo: Valor opcional para el código. Si no se proporciona, se generará automáticamente
        guardar_en_db: Si es True, guarda la información en la base de datos
        
    Returns:
        Diccionario con información sobre el código generado
    """
    try:
        # Verificar si el artículo existe
        articulo = get_articulos(db, articulo_id)
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artículo con ID {articulo_id} no encontrado"
            )
            
        # Verificar que el formato solicitado está soportado
        if tipo_codigo.lower() not in BARCODE_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de código de barras no soportado. Formatos válidos: {list(BARCODE_FORMATS.keys())}"
            )
            
        formato = BARCODE_FORMATS[tipo_codigo.lower()]
        
        # Si no se proporciona un valor, generamos uno basado en el ID y un timestamp
        if not valor_codigo:
            if tipo_codigo.lower() == 'ean13':
                # Para EAN13 necesitamos 12 dígitos (el dígito de verificación se añade automáticamente)
                timestamp = int(datetime.now().timestamp())
                # Combinar ID de artículo y timestamp, asegurando 12 dígitos
                valor_codigo = f"{articulo_id:04d}{timestamp % 100000000:08d}"
            elif tipo_codigo.lower() == 'ean8':
                # Para EAN8 necesitamos 7 dígitos
                timestamp = int(datetime.now().timestamp())
                valor_codigo = f"{articulo_id % 1000:03d}{timestamp % 10000:04d}"
            else:
                # Para otros formatos usamos una combinación del ID y el código del artículo
                valor_codigo = f"{articulo.codigo}-{articulo_id}"
        
        # Generar nombre de archivo único
        filename = f"{uuid.uuid4()}"
        ruta_archivo = BARCODE_DIR / filename
        
        # Generar código de barras
        codigo_barras = formato(valor_codigo, writer=ImageWriter())
        path_imagen = codigo_barras.save(str(ruta_archivo))
        
        # Obtener la ruta relativa para guardar en la base de datos y devolver al cliente
        ruta_relativa = f"/images/codigos/barcode/{os.path.basename(path_imagen)}"
        
        # Si se requiere, guardar la información en la base de datos
        if guardar_en_db:
            datos_actualizacion = {
                "codigo_barras": valor_codigo,
                "codigo_barras_tipo": tipo_codigo,
                "imagen_codigo_url": ruta_relativa
            }
            update_articulos(db, articulo_id, datos_actualizacion)
        
        return {
            "success": True,
            "articulo_id": articulo_id,
            "tipo_codigo": tipo_codigo,
            "valor": valor_codigo,
            "imagen_url": ruta_relativa
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar código de barras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código de barras: {str(e)}"
        )


def generar_codigo_qr(
    db: Session, 
    articulo_id: int, 
    datos: str, 
    version: Optional[int] = None,
    box_size: int = 10,
    border: int = 4,
    guardar_en_db: bool = True
) -> Dict[str, Any]:
    """
    Genera un código QR para un artículo
    
    Args:
        db: Sesión de base de datos
        articulo_id: ID del artículo
        datos: Datos a codificar en el QR (puede ser JSON)
        version: Versión del QR (1-40)
        box_size: Tamaño de cada caja del QR
        border: Borde del QR
        guardar_en_db: Si es True, guarda la información en la base de datos
        
    Returns:
        Diccionario con información sobre el QR generado
    """
    try:
        # Verificar si el artículo existe
        articulo = get_articulos(db, articulo_id)
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artículo con ID {articulo_id} no encontrado"
            )
            
        # Crear el objeto QR con las configuraciones especificadas
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        
        # Añadir los datos al QR
        qr.add_data(datos)
        qr.make(fit=True)
        
        # Crear la imagen
        imagen = qr.make_image(fill_color="black", back_color="white")
        
        # Generar nombre de archivo único
        filename = f"{uuid.uuid4()}.png"
        ruta_archivo = QR_DIR / filename
        
        # Guardar la imagen
        imagen.save(ruta_archivo)
        
        # Obtener la ruta relativa para guardar en la base de datos y devolver al cliente
        ruta_relativa = f"/images/codigos/qr/{filename}"
        
        # Si se requiere, guardar la información en la base de datos
        if guardar_en_db:
            datos_actualizacion = {
                "qr_data": datos,
                "imagen_codigo_url": ruta_relativa
            }
            update_articulos(db, articulo_id, datos_actualizacion)
        
        return {
            "success": True,
            "articulo_id": articulo_id,
            "qr_data": datos,
            "imagen_url": ruta_relativa
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar código QR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código QR: {str(e)}"
        )


def generar_etiqueta_completa(
    db: Session,
    articulo_id: int,
    incluir_codigo_barras: bool = True,
    incluir_qr: bool = True,
    formato_cb: str = "ean13",
    datos_adicionales: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Genera una etiqueta completa con código de barras y/o QR para un artículo
    
    Args:
        db: Sesión de base de datos
        articulo_id: ID del artículo
        incluir_codigo_barras: Si se debe incluir código de barras
        incluir_qr: Si se debe incluir código QR
        formato_cb: Formato del código de barras
        datos_adicionales: Datos adicionales para incluir en el QR
        
    Returns:
        Diccionario con URLs de las imágenes generadas y datos del artículo
    """
    try:
        # Verificar si el artículo existe
        articulo = get_articulos(db, articulo_id)
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artículo con ID {articulo_id} no encontrado"
            )
            
        resultado = {
            "articulo_id": articulo_id,
            "descripcion": articulo.descripcion,
            "codigo": articulo.codigo,
            "precio": articulo.precioventa,
        }
        
        # Generar código de barras si se solicita
        if incluir_codigo_barras:
            codigo_barras = generar_codigo_barras(
                db=db,
                articulo_id=articulo_id,
                tipo_codigo=formato_cb,
                guardar_en_db=True
            )
            resultado["codigo_barras"] = codigo_barras
        
        # Generar QR si se solicita
        if incluir_qr:
            # Crear datos para el QR (información del artículo + datos adicionales)
            qr_datos = {
                "id": articulo_id,
                "codigo": articulo.codigo,
                "descripcion": articulo.descripcion,
                "precio": articulo.precioventa
            }
            
            # Añadir datos adicionales si se proporcionan
            if datos_adicionales:
                qr_datos.update(datos_adicionales)
                
            qr_info = generar_codigo_qr(
                db=db, 
                articulo_id=articulo_id, 
                datos=json.dumps(qr_datos),
                guardar_en_db=True
            )
            resultado["qr"] = qr_info
        
        return resultado
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar etiqueta completa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar etiqueta completa: {str(e)}"
        )