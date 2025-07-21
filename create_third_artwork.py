#!/usr/bin/env python3
"""Script para crear una tercera obra con la segunda imagen"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_third_artwork():
    """Crear tercera obra con segunda imagen"""
    print("=== CREANDO TERCERA OBRA CON SEGUNDA IMAGEN ===\n")
    
    # Subir la segunda imagen
    print("📤 Subiendo segunda imagen...")
    
    with open("segunda_obra.png", 'rb') as image_file:
        files = {'file': ('segunda_obra.png', image_file, 'image/png')}
        upload_response = requests.post(f"{BASE_URL}/app_obras/artworks/upload-image/", files=files)
    
    if upload_response.status_code == 200:
        upload_result = upload_response.json()
        image_url = upload_result['url']
        print(f"✅ Segunda imagen subida: {image_url}")
    else:
        print(f"❌ Error al subir imagen: {upload_response.status_code}")
        return
    
    # Crear obra con Vincent van Gogh
    artwork_data = {
        "inventory_code": "VVG.2025.002",
        "title": "Círculos de Esperanza",
        "nickname": "Los Círculos",
        "creation_year": 2025,
        "technique": "Arte digital moderno",
        "materials": "Píxeles RGB, algoritmos de color",
        "dimensions": "500x400 píxeles",
        "photo_credit": "Generación automática",
        "thumbnail_url": image_url,
        "technical_sheet_url": None,
        "internal_notes": "Obra inspirada en formas geométricas concéntricas, segundo test del sistema",
        "is_available": True,
        "is_sold": False,
        "is_secondary_market": False,
        "artist_id": 2,  # Vincent van Gogh
        "state_id": 2    # Buen estado
    }
    
    print("📝 Creando tercera obra...")
    
    create_response = requests.post(
        f"{BASE_URL}/app_obras/artworks/",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(artwork_data)
    )
    
    if create_response.status_code == 201:
        created_artwork = create_response.json()
        print(f"✅ Tercera obra creada:")
        print(f"   ID: {created_artwork['id']}")
        print(f"   Título: {created_artwork['title']}")
        print(f"   Artista ID: {created_artwork['artist_id']}")
        print(f"   URL Imagen: {created_artwork['thumbnail_url']}")
    else:
        print(f"❌ Error al crear obra: {create_response.status_code}")
        print(f"   Respuesta: {create_response.text}")

if __name__ == "__main__":
    create_third_artwork()
