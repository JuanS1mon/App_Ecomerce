#!/usr/bin/env python3
"""Script para monitorear cambios en la base de datos"""

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine
import time
import os

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def monitor_database():
    """Monitorear cambios en tiempo real"""
    print("=== MONITOR DE BASE DE DATOS EN TIEMPO REAL ===")
    print("Presiona Ctrl+C para detener\n")
    
    last_count = 0
    last_files_count = {"original": 0, "medium": 0, "thumbnails": 0}
    
    try:
        while True:
            db = SessionLocal()
            try:
                # Contar obras
                result = db.execute(text("SELECT COUNT(*) FROM artworks"))
                current_count = result.scalar()
                
                # Contar archivos físicos
                upload_dir = "sql_app/static/uploads/artworks"
                current_files_count = {}
                
                for subdir in ["original", "medium", "thumbnails"]:
                    dir_path = os.path.join(upload_dir, subdir)
                    if os.path.exists(dir_path):
                        current_files_count[subdir] = len(os.listdir(dir_path))
                    else:
                        current_files_count[subdir] = 0
                
                # Detectar cambios
                if current_count != last_count:
                    print(f"🔄 CAMBIO DETECTADO: {current_count} obras (antes: {last_count})")
                    
                    # Mostrar la nueva obra
                    if current_count > last_count:
                        result = db.execute(text("""
                            SELECT 
                                a.id,
                                a.inventory_code,
                                a.title,
                                a.thumbnail_url,
                                art.full_name
                            FROM artworks a
                            LEFT JOIN artists art ON a.artist_id = art.id
                            WHERE a.id = (SELECT MAX(id) FROM artworks)
                        """))
                        
                        row = result.fetchone()
                        if row:
                            print(f"   ✅ Nueva obra creada:")
                            print(f"      ID: {row[0]}")
                            print(f"      Código: {row[1]}")
                            print(f"      Título: {row[2]}")
                            print(f"      Imagen: {row[3]}")
                            print(f"      Artista: {row[4]}")
                    
                    last_count = current_count
                
                # Detectar cambios en archivos
                for subdir in ["original", "medium", "thumbnails"]:
                    if current_files_count[subdir] != last_files_count[subdir]:
                        print(f"📁 ARCHIVOS {subdir.upper()}: {current_files_count[subdir]} (antes: {last_files_count[subdir]})")
                        last_files_count[subdir] = current_files_count[subdir]
                
                # Estado actual
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] 📊 Obras: {current_count} | Archivos: O:{current_files_count['original']} M:{current_files_count['medium']} T:{current_files_count['thumbnails']}", end="\r")
                
            finally:
                db.close()
            
            time.sleep(2)  # Esperar 2 segundos
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en monitor: {e}")

if __name__ == "__main__":
    monitor_database()
