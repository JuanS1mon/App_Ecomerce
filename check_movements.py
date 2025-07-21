#!/usr/bin/env python3
"""
Script para verificar los movimientos creados
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "sql_app"))

from sqlalchemy import create_engine, text
from sql_app.db.database import SQLALCHEMY_DATABASE_URL

def check_movements():
    """Verificar movimientos en la base de datos"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Contar movimientos
            result = conn.execute(text("SELECT COUNT(*) as total FROM movements"))
            total = result.fetchone().total
            print(f"📊 Total de movimientos: {total}")
            
            # Movimientos por tipo
            result = conn.execute(text("""
                SELECT movement_type, COUNT(*) as count 
                FROM movements 
                GROUP BY movement_type
            """))
            print("\n📈 Movimientos por tipo:")
            for row in result.fetchall():
                print(f"   {row.movement_type.upper()}: {row.count}")
            
            # Movimientos por estado
            result = conn.execute(text("""
                SELECT status, COUNT(*) as count 
                FROM movements 
                GROUP BY status
            """))
            print("\n🔄 Movimientos por estado:")
            for row in result.fetchall():
                print(f"   {row.status.upper()}: {row.count}")
            
            # Movimientos recientes
            result = conn.execute(text("""
                SELECT TOP 3 id, movement_type, notes, contact_name, start_date
                FROM movements 
                ORDER BY id DESC
            """))
            print("\n🕒 Movimientos más recientes:")
            for row in result.fetchall():
                print(f"   #{row.id}: {row.movement_type.upper()} - {row.notes[:40]}...")
                print(f"      👤 {row.contact_name}")
                print(f"      📅 {row.start_date}")
                print()
                
    except Exception as e:
        print(f"❌ Error al verificar movimientos: {e}")

if __name__ == "__main__":
    check_movements()
