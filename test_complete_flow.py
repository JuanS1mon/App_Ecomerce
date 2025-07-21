#!/usr/bin/env python3
"""Script para probar la creación de obra con imagen y ver el resultado en SQL"""

import requests
import json
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine
import os

# Configuración
BASE_URL = "http://localhost:8000"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_image_upload_and_artwork_creation():
    """Probar el flujo completo de subida de imagen y creación de obra"""
    print("=== PRUEBA COMPLETA DE CREACIÓN DE OBRA CON IMAGEN ===\n")
    
    # Verificar que la imagen existe
    image_path = "obra_prueba.jpg"
    if not os.path.exists(image_path):
        print("❌ No se encontró la imagen de prueba")
        return
    
    try:
        # Paso 1: Subir imagen
        print("📤 Paso 1: Subiendo imagen...")
        
        with open(image_path, 'rb') as image_file:
            files = {'file': ('obra_prueba.jpg', image_file, 'image/jpeg')}
            upload_response = requests.post(f"{BASE_URL}/app_obras/artworks/upload-image/", files=files)
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            image_url = upload_result['url']
            print(f"✅ Imagen subida exitosamente: {image_url}")
            print(f"   Respuesta completa: {upload_result}")
        else:
            print(f"❌ Error al subir imagen: {upload_response.status_code}")
            print(f"   Respuesta: {upload_response.text}")
            return
        
        print()
        
        # Paso 2: Crear obra de arte
        print("📝 Paso 2: Creando obra de arte...")
        
        artwork_data = {
            "inventory_code": "TEST.2025.001",
            "title": "Obra de Prueba Digital",
            "nickname": "La Prueba",
            "creation_year": 2025,
            "technique": "Arte digital",
            "materials": "Píxeles, código, imaginación",
            "dimensions": "400x300 píxeles",
            "photo_credit": "Sistema automatizado",
            "thumbnail_url": image_url,  # URL de la imagen subida
            "technical_sheet_url": None,
            "internal_notes": "Obra creada automáticamente para pruebas del sistema",
            "is_available": True,
            "is_sold": False,
            "is_secondary_market": False,
            "artist_id": 1,  # Pablo Picasso
            "state_id": 1    # Excelente estado
        }
        
        create_response = requests.post(
            f"{BASE_URL}/app_obras/artworks/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(artwork_data)
        )
        
        if create_response.status_code == 201:
            created_artwork = create_response.json()
            print(f"✅ Obra creada exitosamente:")
            print(f"   ID: {created_artwork['id']}")
            print(f"   Título: {created_artwork['title']}")
            print(f"   Código: {created_artwork['inventory_code']}")
            print(f"   URL Imagen: {created_artwork['thumbnail_url']}")
            
            artwork_id = created_artwork['id']
        else:
            print(f"❌ Error al crear obra: {create_response.status_code}")
            print(f"   Respuesta: {create_response.text}")
            return
        
        print()
        
        # Paso 3: Verificar en la base de datos
        print("🔍 Paso 3: Verificando en la base de datos...")
        
        db = SessionLocal()
        try:
            # Consultar la obra recién creada
            result = db.execute(text("""
                SELECT 
                    a.id,
                    a.inventory_code,
                    a.title,
                    a.nickname,
                    a.creation_year,
                    a.technique,
                    a.materials,
                    a.dimensions,
                    a.thumbnail_url,
                    a.internal_notes,
                    a.is_available,
                    a.is_sold,
                    art.full_name as artist_name,
                    s.description as state_description
                FROM artworks a
                LEFT JOIN artists art ON a.artist_id = art.id
                LEFT JOIN artwork_states s ON a.state_id = s.id
                WHERE a.id = :artwork_id
            """), {"artwork_id": artwork_id})
            
            row = result.fetchone()
            if row:
                print("✅ Datos en la base de datos:")
                print(f"   🆔 ID: {row[0]}")
                print(f"   📋 Código: {row[1]}")
                print(f"   🎨 Título: {row[2]}")
                print(f"   💝 Nickname: {row[3]}")
                print(f"   📅 Año: {row[4]}")
                print(f"   🎭 Técnica: {row[5]}")
                print(f"   🧱 Materiales: {row[6]}")
                print(f"   📏 Dimensiones: {row[7]}")
                print(f"   🖼️ URL Imagen: {row[8]}")
                print(f"   📝 Notas: {row[9]}")
                print(f"   ✅ Disponible: {row[10]}")
                print(f"   💰 Vendida: {row[11]}")
                print(f"   👨‍🎨 Artista: {row[12]}")
                print(f"   🏷️ Estado: {row[13]}")
            else:
                print("❌ No se encontró la obra en la base de datos")
                
        finally:
            db.close()
        
        print()
        
        # Paso 4: Verificar archivos físicos
        print("📂 Paso 4: Verificando archivos físicos...")
        
        upload_dir = "sql_app/static/uploads/artworks"
        subdirs = ["original", "medium", "thumbnails"]
        
        for subdir in subdirs:
            dir_path = os.path.join(upload_dir, subdir)
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                print(f"   📁 {subdir}: {len(files)} archivo(s)")
                for file in files[-1:]:  # Mostrar el último archivo
                    file_path = os.path.join(dir_path, file)
                    size = os.path.getsize(file_path)
                    print(f"      - {file} ({size} bytes)")
            else:
                print(f"   ❌ Directorio {subdir} no existe")
        
        print()
        print("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
        print(f"   Puedes ver la obra en: {BASE_URL}/app_obras/artworks/html/")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_upload_and_artwork_creation()
