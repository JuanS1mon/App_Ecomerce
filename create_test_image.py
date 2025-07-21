#!/usr/bin/env python3
"""Script para crear una imagen de prueba"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """Crear una imagen de prueba para subir"""
    # Crear una imagen de 400x300 píxeles
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='#f0f0f0')
    
    # Obtener un objeto de dibujo
    draw = ImageDraw.Draw(image)
    
    # Dibujar un rectángulo de color
    draw.rectangle([50, 50, width-50, height-50], fill='#4a90e2', outline='#2c5aa0', width=3)
    
    # Intentar agregar texto
    try:
        # Usar fuente por defecto si no encuentra una específica
        font = ImageFont.load_default()
        text = "OBRA DE PRUEBA"
        
        # Calcular posición centrada del texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        
    except Exception as e:
        print(f"No se pudo agregar texto: {e}")
    
    # Guardar la imagen
    filename = "obra_prueba.jpg"
    image.save(filename, "JPEG", quality=85)
    print(f"✅ Imagen de prueba creada: {filename}")
    return filename

if __name__ == "__main__":
    create_test_image()
