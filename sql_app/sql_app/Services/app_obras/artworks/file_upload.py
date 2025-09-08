# Imports de terceros
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import os
import uuid
import shutil
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

# Configuración
UPLOAD_DIR = Path("sql_app/static/uploads/artworks")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def ensure_upload_directories():
    """Crear directorios de subida si no existen"""
    directories = [
        UPLOAD_DIR / "original",
        UPLOAD_DIR / "medium", 
        UPLOAD_DIR / "thumbnails"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def validate_image_file(file: UploadFile) -> bool:
    """Validar archivo de imagen"""
    # Validar extensión
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tipo MIME
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    
    return True

def generate_unique_filename(original_filename: str) -> str:
    """Generar nombre único para el archivo"""
    file_extension = Path(original_filename).suffix.lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

def resize_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Redimensionar imagen manteniendo proporción"""
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

async def process_and_save_image(file: UploadFile) -> dict:
    """Procesar y guardar imagen en diferentes tamaños"""
    try:
        # Validar archivo
        validate_image_file(file)
        
        # Asegurar que existen los directorios
        ensure_upload_directories()
        
        # Generar nombre único
        unique_filename = generate_unique_filename(file.filename)
        
        # Leer contenido del archivo
        contents = await file.read()
        
        # Validar tamaño
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo demasiado grande. Máximo {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        # Abrir imagen con PIL
        try:
            with Image.open(io.BytesIO(contents)) as image:
                # Convertir a RGB si es necesario
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                
                # Guardar imagen original
                original_path = UPLOAD_DIR / "original" / unique_filename
                image.save(original_path, "JPEG", quality=95)
                
                # Crear versión mediana (800x600)
                medium_image = resize_image(image.copy(), 800, 600)
                medium_path = UPLOAD_DIR / "medium" / unique_filename
                medium_image.save(medium_path, "JPEG", quality=85)
                
                # Crear thumbnail (300x300)
                thumbnail_image = resize_image(image.copy(), 300, 300)
                thumbnail_path = UPLOAD_DIR / "thumbnails" / unique_filename
                thumbnail_image.save(thumbnail_path, "JPEG", quality=80)
                
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al procesar la imagen. Asegúrate de que sea un archivo de imagen válido."
            )
        
        # Construir URLs relativas
        base_url = "/static/uploads/artworks"
        result = {
            "filename": unique_filename,
            "original_url": f"{base_url}/original/{unique_filename}",
            "medium_url": f"{base_url}/medium/{unique_filename}",
            "thumbnail_url": f"{base_url}/thumbnails/{unique_filename}",
            "size": len(contents)
        }
        
        logger.info(f"Imagen procesada exitosamente: {unique_filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al procesar imagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la imagen"
        )

def delete_artwork_images(filename: str):
    """Eliminar todas las versiones de una imagen"""
    try:
        paths_to_delete = [
            UPLOAD_DIR / "original" / filename,
            UPLOAD_DIR / "medium" / filename,
            UPLOAD_DIR / "thumbnails" / filename
        ]
        
        for path in paths_to_delete:
            if path.exists():
                path.unlink()
                logger.info(f"Imagen eliminada: {path}")
                
    except Exception as e:
        logger.error(f"Error eliminando imágenes: {e}")

# Importar io para BytesIO
import io
