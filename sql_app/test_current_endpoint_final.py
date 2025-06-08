#!/usr/bin/env python3
"""
Script para probar el endpoint /usuarios/current con token JWT válido
"""
import requests
import json
from datetime import datetime, timedelta
from jose import jwt

# Configuración del servidor (debe coincidir con el servidor)
BASE_URL = "http://localhost:8001"
SECRET_KEY = "tu_clave_secreta_aqui"
ALGORITHM = "HS256"

def create_test_token():
    """Crea un token JWT de prueba"""
    # Datos del usuario de prueba
    user_data = {
        "codigo": 1,
        "mail": "test@example.com", 
        "nombre": "Usuario de Prueba",
        "sub": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_current_endpoint_with_token():
    """Prueba el endpoint /usuarios/current con token válido"""
    print("🧪 Probando endpoint /usuarios/current con token JWT...")
    
    # Crear token de prueba
    token = create_test_token()
    print(f"✅ Token JWT creado: {token[:50]}...")
    
    # Headers con el token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Hacer la solicitud
        response = requests.get(f"{BASE_URL}/usuarios/current", headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ ¡Éxito! El endpoint devolvió datos del usuario:")
            try:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("📄 Contenido de respuesta:")
                print(response.text[:500])
        else:
            print(f"❌ Error: {response.status_code}")
            print("📄 Contenido de respuesta:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Error en la solicitud: {e}")

def test_current_endpoint_without_token():
    """Prueba el endpoint /usuarios/current sin token (debe redirigir)"""
    print("\n🧪 Probando endpoint /usuarios/current sin token...")
    
    try:
        # Hacer la solicitud sin token (no seguir redirects)
        response = requests.get(f"{BASE_URL}/usuarios/current", allow_redirects=False)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 307:
            print("✅ ¡Correcto! Redirección a login como se esperaba")
            print(f"🔗 Location: {response.headers.get('location', 'No location header')}")
        else:
            print(f"❌ Comportamiento inesperado: {response.status_code}")
            print("📄 Contenido:")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Error en la solicitud: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del endpoint /usuarios/current")
    print("=" * 60)
    
    # Probar sin token (debe redirigir)
    test_current_endpoint_without_token()
    
    # Probar con token (debe devolver datos)
    test_current_endpoint_with_token()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
