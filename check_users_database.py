#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos y sus contraseñas hasheadas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_app.database import get_db
from sql_app.models import User
from sqlalchemy.orm import Session

def check_users():
    """Verifica todos los usuarios en la base de datos"""
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        users = db.query(User).all()
        print(f"Total de usuarios encontrados: {len(users)}")
        print("-" * 50)
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Is Active: {user.is_active}")
            print(f"Is Admin: {getattr(user, 'is_admin', 'N/A')}")
            print(f"Hashed Password: {user.hashed_password[:50]}..." if user.hashed_password else "Sin contraseña")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error al consultar usuarios: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
