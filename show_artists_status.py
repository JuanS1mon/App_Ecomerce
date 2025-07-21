#!/usr/bin/env python3
"""Script para mostrar el estado final del sistema de artistas"""

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def show_artists_status():
    """Mostrar el estado actual del sistema de artistas"""
    print("=== ESTADO FINAL DEL SISTEMA DE ARTISTAS ===\n")
    
    db = SessionLocal()
    try:
        # Mostrar todos los artistas
        print("👨‍🎨 LISTADO COMPLETO DE ARTISTAS:")
        result = db.execute(text("""
            SELECT 
                id,
                full_name
            FROM artists 
            ORDER BY id
        """))
        
        artists = result.fetchall()
        
        for artist in artists:
            print(f"   • ID {artist[0]}: {artist[1]}")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total de artistas: {len(artists)}")
        
        # Verificar obras por artista
        print(f"\n🎨 OBRAS POR ARTISTA:")
        result = db.execute(text("""
            SELECT 
                a.full_name,
                COUNT(aw.id) as total_obras
            FROM artists a
            LEFT JOIN artworks aw ON a.id = aw.artist_id
            GROUP BY a.id, a.full_name
            ORDER BY COUNT(aw.id) DESC, a.full_name
        """))
        
        for row in result:
            obras_text = f"{row[1]} obra(s)" if row[1] > 0 else "Sin obras"
            status_icon = "🎨" if row[1] > 0 else "📝"
            print(f"   {status_icon} {row[0]}: {obras_text}")
        
        print(f"\n🌐 ACCESO WEB:")
        print(f"   • Listado: http://localhost:8000/app_obras/artists/html/")
        print(f"   • Crear nuevo: http://localhost:8000/app_obras/artists/html/create/")
        print(f"   • API: http://localhost:8000/app_obras/artists/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_artists_status()
