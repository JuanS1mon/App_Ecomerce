#!/usr/bin/env python3
"""
Script para crear un usuario de prueba para ecommerce
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from security.ecommerce_auth import register_ecommerce_user
from sqlalchemy.orm import Session

def create_test_ecommerce_user():
    """Crear usuario de prueba para ecommerce"""
    db: Session = next(get_db())

    try:
        # Datos del usuario de prueba
        test_user_data = {
            "nombre": "Usuario",
            "apellido": "Prueba",
            "email": "test@example.com",
            "contraseña": "test123",
            "telefono": "123456789",
            "direccion": "Calle de Prueba 123",
            "ciudad": "Ciudad de Prueba",
            "provincia": "Provincia de Prueba",
            "pais": "País de Prueba"
        }

        # Registrar usuario
        result = register_ecommerce_user(db, test_user_data)

        if result:
            print("✅ Usuario ecommerce de prueba creado exitosamente!")
            print(f"📧 Email: {test_user_data['email']}")
            print(f"🔑 Contraseña: {test_user_data['contraseña']}")
            print(f"👤 Nombre: {result['nombre']} {result['apellido']}")
            print(f"🆔 ID: {result['id']}")
        else:
            print("❌ Error al crear usuario de prueba")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_ecommerce_user()