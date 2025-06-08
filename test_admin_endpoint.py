#!/usr/bin/env python3
"""Script para probar el endpoint /admin y verificar la carga de plantillas"""

import requests
import sys

def test_admin_endpoint():
    base_url = "http://127.0.0.1:8000"
    
    # Paso 1: Realizar login
    print("🔐 Probando login...")
    login_data = {
        'username': 'testuser',
        'password': 'Test123456'
    }
    
    try:
        login_response = requests.post(f"{base_url}/login", data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.text}")
            return False
            
        # Extraer token
        token_data = login_response.json()
        token = token_data.get('access_token')
        
        if not token:
            print("❌ No se pudo obtener el token")
            return False
            
        print(f"✅ Token obtenido: {token[:30]}...")
        
        # Paso 2: Probar endpoint /admin
        print("🔧 Probando endpoint /admin...")
        headers = {'Authorization': f'Bearer {token}'}
        
        admin_response = requests.get(f"{base_url}/admin", headers=headers)
        print(f"Admin status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("✅ ¡Endpoint /admin funcionando! Plantilla cargada exitosamente.")
            print(f"Content-Type: {admin_response.headers.get('content-type')}")
            print(f"Tamaño de respuesta: {len(admin_response.content)} bytes")
            return True
        else:
            print(f"❌ Error en /admin: {admin_response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está corriendo en http://127.0.0.1:8000?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_endpoint()
    sys.exit(0 if success else 1)
