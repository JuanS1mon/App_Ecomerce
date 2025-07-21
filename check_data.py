#!/usr/bin/env python3
"""Script para verificar datos básicos en la base de datos"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine
# Solo importar los modelos básicos
from sqlalchemy import text

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_basic_data():
    """Verificar datos básicos necesarios"""
    print("=== VERIFICACIÓN DE DATOS BÁSICOS ===\n")
    
    # Usar queries SQL directas para evitar problemas de relaciones
    # Verificar artistas
    result = db.execute(text("SELECT COUNT(*) FROM artists"))
    artists_count = result.scalar()
    print(f"Artistas en la base de datos: {artists_count}")
    
    if artists_count > 0:
        result = db.execute(text("SELECT TOP 5 id, full_name FROM artists"))
        for row in result:
            print(f"  - ID: {row[0]}, Nombre: {row[1]}")
    print()
    
    # Verificar estados de obra
    result = db.execute(text("SELECT COUNT(*) FROM artwork_states"))
    states_count = result.scalar()
    print(f"Estados de obra en la base de datos: {states_count}")
    
    if states_count > 0:
        result = db.execute(text("SELECT TOP 5 id, description FROM artwork_states"))
        for row in result:
            print(f"  - ID: {row[0]}, Descripción: {row[1]}")
    print()
    
    # Verificar obras existentes
    result = db.execute(text("SELECT COUNT(*) FROM artworks"))
    artworks_count = result.scalar()
    print(f"Obras de arte en la base de datos: {artworks_count}")
    
    if artworks_count > 0:
        result = db.execute(text("SELECT TOP 3 id, title, thumbnail_url FROM artworks"))
        for row in result:
            print(f"  - ID: {row[0]}, Título: {row[1]}, Imagen: {row[2]}")
    print()

if __name__ == "__main__":
    try:
        check_basic_data()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
