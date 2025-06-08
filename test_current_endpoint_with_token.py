#!/usr/bin/env python3
"""
Test script para probar el endpoint /usuarios/current con un token JWT válido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sql_app.main import app
from sql_app.Services.security.security import crear_access_token, SECRET, ALGORITHM
from sql_app.db.database import SessionLocal, engine
from sql_app.db.models.config.usuarios import usuarios
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta
from jose import jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_test_user_if_not_exists():
    """Crear un usuario de prueba si no existe"""
    db = SessionLocal()
    try:        # Buscar usuario existente
        user = db.query(usuarios).filter(usuarios.mail == "test@example.com").first()
        if user:
            print(f"Usuario de prueba encontrado: ID={user.codigo}, Email={user.mail}")
            return user
        
        # Crear usuario de prueba
        print("Creando usuario de prueba...")        new_user = usuarios(
            nombre="Test User",
            usuario="testuser",
            mail="test@example.com",
            clave="$2b$12$dummy_hash",  # Hash dummy para pruebas
            activo=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Usuario de prueba creado: ID={new_user.codigo}, Email={new_user.mail}")
        return new_user
        
    except Exception as e:
        print(f"Error creando usuario de prueba: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_valid_token(user_id: int, email: str):
    """Crear un token JWT válido para el usuario"""
    try:        # Datos del token
        data = {
            "sub": str(user_id),
            "email": email,
            "type": "access"
        }
        
        # Crear token usando la función existente
        token = crear_access_token(data)
        print(f"Token creado exitosamente para usuario {user_id}")
        print(f"Token: {token[:50]}...")
        return token
        
    except Exception as e:
        print(f"Error creando token: {e}")
        return None

def test_endpoint_with_token():
    """Probar el endpoint /usuarios/current con token válido"""
    
    print("=" * 60)
    print("PROBANDO /usuarios/current CON TOKEN VÁLIDO")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = TestClient(app)
    
    # Crear usuario de prueba
    test_user = create_test_user_if_not_exists()
    if not test_user:
        print("❌ No se pudo crear usuario de prueba")
        return
    
    # Crear token válido
    token = create_valid_token(test_user.id, test_user.email)
    if not token:
        print("❌ No se pudo crear token válido")
        return
    
    # Probar endpoint con token
    print("\n1. Probando endpoint con token en Authorization header...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/usuarios/current", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa!")
            try:
                data = response.json()
                print(f"Datos del usuario: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # Verificar que no es el usuario "invitado"
                if data.get("nombre") == "Invitado":
                    print("⚠️  PROBLEMA: Aún devuelve usuario 'Invitado'")
                else:
                    print("✅ Devuelve datos de usuario reales, no 'Invitado'")
                    
            except Exception as e:
                print(f"Error parseando JSON: {e}")
                print(f"Contenido de respuesta: {response.text}")
        else:
            print(f"❌ Error en respuesta: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Contenido: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
    
    # Probar también sin token para comparar
    print("\n2. Probando endpoint SIN token (para comparar)...")
    try:
        response = client.get("/usuarios/current")
        print(f"Status Code sin token: {response.status_code}")
        if response.status_code == 307:
            print("✅ Redirige a login sin token (comportamiento esperado)")
        else:
            print(f"Respuesta sin token: {response.text[:200]}...")
    except Exception as e:
        print(f"Error en prueba sin token: {e}")

def test_token_validation():
    """Probar la validación de tokens directamente"""
    print("\n" + "=" * 60)
    print("PROBANDO VALIDACIÓN DE TOKENS DIRECTAMENTE")  
    print("=" * 60)
    
    # Crear usuario de prueba
    test_user = create_test_user_if_not_exists()
    if not test_user:
        return
    
    # Crear token válido
    token = create_valid_token(test_user.id, test_user.email)
    if not token:
        return
    
    # Probar decodificación del token
    try:
        from sql_app.Services.security.security import decodifica_token
        
        print("Probando decodificación de token...")
        decoded = decodifica_token(token)
        print(f"Token decodificado: {decoded}")
        
        if decoded:
            print("✅ Token se decodifica correctamente")
        else:
            print("❌ Token no se pudo decodificar")
            
    except Exception as e:
        print(f"❌ Error en decodificación: {e}")

if __name__ == "__main__":
    print("Iniciando pruebas del endpoint /usuarios/current...")
    
    # Probar validación de tokens
    test_token_validation()
    
    # Probar endpoint con token
    test_endpoint_with_token()
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)
