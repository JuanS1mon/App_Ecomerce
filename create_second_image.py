#!/usr/bin/env python3
"""Script para crear una segunda imagen de prueba diferente"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_second_test_image():
    """Crear una segunda imagen de prueba"""
    # Crear una imagen de 500x400 píxeles
    width, height = 500, 400
    image = Image.new('RGB', (width, height), color='#2c3e50')
    
    # Obtener un objeto de dibujo
    draw = ImageDraw.Draw(image)
    
    # Dibujar círculos concéntricos
    center_x, center_y = width // 2, height // 2
    colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#3498db']
    
    for i, color in enumerate(colors):
        radius = 150 - (i * 25)
        if radius > 0:
            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius], 
                fill=color
            )
    
    # Intentar agregar texto
    try:
        font = ImageFont.load_default()
        text = "SEGUNDA OBRA"
        
        # Calcular posición centrada del texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2 + 50
        
        # Fondo blanco para el texto
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill='white')
        draw.text((x, y), text, fill='black', font=font)
        
    except Exception as e:
        print(f"No se pudo agregar texto: {e}")
    
    # Guardar la imagen
    filename = "segunda_obra.png"
    image.save(filename, "PNG")
    print(f"✅ Segunda imagen de prueba creada: {filename}")
    return filename

if __name__ == "__main__":
    create_second_test_image()
