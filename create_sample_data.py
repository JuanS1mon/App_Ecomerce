#!/usr/bin/env python3
"""Script para crear datos básicos de prueba"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine
from sqlalchemy import text

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_sample_data():
    """Crear datos de ejemplo"""
    print("=== CREANDO DATOS DE EJEMPLO ===\n")
    
    try:
        # Crear artistas de ejemplo
        artists_data = [
            "Pablo Picasso",
            "Vincent van Gogh",
            "Salvador Dalí",
            "Frida Kahlo",
            "Claude Monet"
        ]
        
        for full_name in artists_data:
            # Verificar si ya existe
            existing = db.execute(text("SELECT id FROM artists WHERE full_name = :full_name"), {"full_name": full_name}).fetchone()
            if not existing:
                db.execute(text("""
                    INSERT INTO artists (full_name) 
                    VALUES (:full_name)
                """), {
                    "full_name": full_name
                })
        
        print("✓ Artistas creados")
        
        # Crear estados de obra de ejemplo
        states_data = [
            "Excelente - Obra en perfecto estado",
            "Bueno - Obra en buen estado general",
            "Regular - Obra con algunas marcas de uso",
            "Restauración necesaria",
            "En restauración"
        ]
        
        for description in states_data:
            # Verificar si ya existe
            existing = db.execute(text("SELECT id FROM artwork_states WHERE description = :description"), {"description": description}).fetchone()
            if not existing:
                db.execute(text("""
                    INSERT INTO artwork_states (description) 
                    VALUES (:description)
                """), {
                    "description": description
                })
        
        print("✓ Estados de obra creados")
        
        # Confirmar los cambios
        db.commit()
        print("\n✅ Datos de ejemplo creados exitosamente!")
        
        # Verificar los datos creados
        print("\n=== VERIFICACIÓN ===")
        result = db.execute(text("SELECT COUNT(*) FROM artists"))
        print(f"Total artistas: {result.scalar()}")
        
        result = db.execute(text("SELECT COUNT(*) FROM artwork_states"))
        print(f"Total estados: {result.scalar()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
