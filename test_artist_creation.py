#!/usr/bin/env python3
"""Script para probar la creación de artista y ver el resultado"""

import requests
import json
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine

BASE_URL = "http://localhost:8000"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_artist_creation():
    """Probar la creación de un nuevo artista"""
    print("=== PRUEBA DE CREACIÓN DE ARTISTA ===\n")
    
    # Datos del nuevo artista
    artist_data = {
        "full_name": "Georgia O'Keeffe"
    }
    
    try:
        # Crear artista
        print("📝 Creando nuevo artista...")
        
        create_response = requests.post(
            f"{BASE_URL}/app_obras/artists/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(artist_data)
        )
        
        if create_response.status_code == 201:
            created_artist = create_response.json()
            print(f"✅ Artista creado exitosamente:")
            print(f"   ID: {created_artist['id']}")
            print(f"   Nombre: {created_artist['full_name']}")
            
            artist_id = created_artist['id']
        else:
            print(f"❌ Error al crear artista: {create_response.status_code}")
            print(f"   Respuesta: {create_response.text}")
            return
        
        print()
        
        # Verificar en la base de datos
        print("🔍 Verificando en la base de datos...")
        
        db = SessionLocal()
        try:
            # Consultar el artista recién creado
            result = db.execute(text("""
                SELECT 
                    id,
                    full_name
                FROM artists 
                WHERE id = :artist_id
            """), {"artist_id": artist_id})
            
            row = result.fetchone()
            if row:
                print("✅ Datos en la base de datos:")
                print(f"   🆔 ID: {row[0]}")
                print(f"   👨‍🎨 Nombre: {row[1]}")
            else:
                print("❌ No se encontró el artista en la base de datos")
            
            # Verificar total de artistas
            result = db.execute(text("SELECT COUNT(*) FROM artists"))
            total_artists = result.scalar()
            print(f"\n📊 Total de artistas en el sistema: {total_artists}")
                
        finally:
            db.close()
        
        print()
        print("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
        print(f"   Puedes ver el artista en: {BASE_URL}/app_obras/artists/html/")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_artist_creation()
