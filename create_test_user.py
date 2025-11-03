#!/usr/bin/env python3
"""
Script para crear un usuario de prueba para testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models.config.usuarios import Usuarios
from security.security import encriptar_clave
from sqlalchemy.orm import Session

def create_test_user():
    """Crear usuario de prueba"""
    db: Session = next(get_db())

    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuarios).filter(Usuarios.usuario == "test_admin").first()
        if existing_user:
            print("Usuario 'test_admin' ya existe")
            return

        # Crear usuario de prueba
        hashed_password = encriptar_clave("test123")

        new_user = Usuarios(
            usuario="test_admin",
            nombre="Usuario de Prueba Admin",
            mail="test@example.com",
            clave=hashed_password,
            activo=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"✅ Usuario 'test_admin' creado exitosamente con ID: {new_user.codigo}")
        print("🔑 Contraseña: test123")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear usuario: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()