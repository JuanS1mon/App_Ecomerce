#!/usr/bin/env python3
"""
Script para crear un usuario de prueba
"""

import sys
import os
sys.path.append('c:/Users/PCJuan/Desktop/sql_app/sql_app')

from sqlalchemy.orm import Session
from db.database import get_db, engine
from db.models.config.usuarios import usuarios as UsuariosModel
from Services.security.security_improved import encriptar_clave
import secrets
import string

def generate_random_password(length=8):
    """Generar una contraseña aleatoria simple"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_test_user():
    """Crear un usuario de prueba"""
    
    # Datos del usuario de prueba
    test_username = "testuser"
    test_password = "Test123456"  # Contraseña simple para testing
    test_email = "test@example.com"
    test_nombre = "Usuario de Prueba"
    
    print(f"🧪 CREANDO USUARIO DE PRUEBA")
    print(f"=" * 40)
    print(f"👤 Usuario: {test_username}")
    print(f"🔐 Contraseña: {test_password}")
    print(f"📧 Email: {test_email}")
    print(f"👨‍💼 Nombre: {test_nombre}")
    print(f"=" * 40)
    
    # Crear sesión de base de datos
    db = next(get_db())
    
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(UsuariosModel).filter(
            (UsuariosModel.usuario == test_username) | 
            (UsuariosModel.mail == test_email)
        ).first()
        
        if existing_user:
            print(f"⚠️  El usuario '{test_username}' ya existe. Eliminando...")
            db.delete(existing_user)
            db.commit()
            print(f"🗑️  Usuario anterior eliminado")
        
        # Encriptar la contraseña
        print(f"🔒 Encriptando contraseña...")
        hashed_password = encriptar_clave(test_password)
        print(f"✅ Contraseña encriptada: {hashed_password[:20]}...")
          # Obtener el próximo código disponible
        max_codigo = db.query(UsuariosModel.codigo).order_by(UsuariosModel.codigo.desc()).first()
        next_codigo = (max_codigo[0] + 1) if max_codigo else 1
        print(f"🆔 Asignando código: {next_codigo}")
        
        # Crear el nuevo usuario
        new_user = UsuariosModel(
            codigo=next_codigo,
            usuario=test_username,
            clave=hashed_password,
            mail=test_email,
            nombre=test_nombre,
            activo=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Usuario creado exitosamente!")
        print(f"🆔 ID del usuario: {new_user.codigo}")
        print(f"👤 Usuario: {new_user.usuario}")
        print(f"📧 Email: {new_user.mail}")
        print(f"✅ Activo: {new_user.activo}")
        
        return {
            'username': test_username,
            'password': test_password,
            'email': test_email,
            'id': new_user.codigo
        }
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def test_user_login(username, password):
    """Probar el login del usuario recién creado"""
    import requests
    
    print(f"\n🔐 PROBANDO LOGIN DEL USUARIO")
    print(f"=" * 40)
    
    url = "http://localhost:8000/login"
    data = {
        'username': username,
        'password': password
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print(f"🚀 Enviando petición POST a: {url}")
        print(f"📊 Datos: username={username}, password=***")
        
        response = requests.post(url, data=data, headers=headers)
        
        print(f"📬 Respuesta recibida:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"✅ LOGIN EXITOSO!")
            print(f"🎫 Token: {response_json.get('access_token', 'No encontrado')[:50]}...")
            print(f"👤 Info del usuario: {response_json.get('user_info', 'No encontrada')}")
            return True
        else:
            print(f"❌ LOGIN FALLIDO!")
            print(f"Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SCRIPT DE CREACIÓN DE USUARIO DE PRUEBA")
    print("=" * 50)
    
    # Crear usuario
    user_info = create_test_user()
    
    if user_info:
        print(f"\n✅ Usuario creado exitosamente!")
        
        # Probar login
        login_success = test_user_login(user_info['username'], user_info['password'])
        
        if login_success:
            print(f"\n🎉 TODO FUNCIONA CORRECTAMENTE!")
            print(f"Puedes usar estas credenciales para probar:")
            print(f"👤 Usuario: {user_info['username']}")
            print(f"🔐 Contraseña: {user_info['password']}")
        else:
            print(f"\n❌ Hay un problema con el sistema de login")
    else:
        print(f"\n❌ No se pudo crear el usuario de prueba")
