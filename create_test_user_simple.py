#!/usr/bin/env python3
"""
Script para crear/actualizar usuario de prueba con credenciales conocidas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

from sqlalchemy.orm import Session
from db.database import engine, get_db
from db.models.config.usuarios import Usuario
from Services.security.security_improved import encriptar_clave

def create_test_user():
    """Crear o actualizar usuario de prueba"""
    
    print("🔧 CREANDO/ACTUALIZANDO USUARIO DE PRUEBA")
    print("=" * 50)
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Credenciales del usuario de prueba
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.usuario == username).first()
        
        if existing_user:
            print(f"📝 Usuario '{username}' ya existe. Actualizando contraseña...")
            # Actualizar contraseña
            existing_user.clave = encriptar_clave(password)
            existing_user.activo = True
            db.commit()
            print(f"✅ Contraseña actualizada para usuario '{username}'")
        else:
            print(f"👤 Creando nuevo usuario '{username}'...")
            # Crear nuevo usuario
            new_user = Usuario(
                usuario=username,
                clave=encriptar_clave(password),
                mail=email,
                nombre=username,
                activo=True
            )
            db.add(new_user)
            db.commit()
            print(f"✅ Usuario '{username}' creado correctamente")
        
        # Verificar que se guardó correctamente
        user = db.query(Usuario).filter(Usuario.usuario == username).first()
        if user:
            print(f"\n📋 Detalles del usuario:")
            print(f"   ID: {user.id}")
            print(f"   Usuario: {user.usuario}")
            print(f"   Email: {user.mail}")
            print(f"   Activo: {user.activo}")
            print(f"   Hash de clave: {user.clave[:30]}...")
            
            print(f"\n🔐 Credenciales para pruebas:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
        else:
            print("❌ Error: No se pudo verificar el usuario")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
