#!/usr/bin/env python3
"""
Script para probar el endpoint /admin con autenticación
"""

import requests
import sys
import json

def test_admin_with_auth():
    """Probar endpoint /admin con token de autorización"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🔧 TESTING ADMIN ENDPOINT WITH AUTHENTICATION")
    print("=" * 50)
    
    # Paso 1: Obtener token de login
    print("\n📝 Paso 1: Obteniendo token de login...")    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/login",
            data=login_data,  # form data
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get("access_token")
            print(f"   ✅ Token obtenido: {token[:50]}...")
            
            # Paso 2: Probar /admin con Authorization header
            print("\n🏢 Paso 2: Probando /admin con Authorization header...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            admin_response = requests.get(f"{BASE_URL}/admin", headers=headers, timeout=10)
            print(f"   Admin Status: {admin_response.status_code}")
            print(f"   Content-Type: {admin_response.headers.get('content-type', 'N/A')}")
            print(f"   Content Length: {len(admin_response.text)}")
            
            # Verificar si es HTML del admin dashboard
            if "SQL App Studio" in admin_response.text:
                print("   ✅ Página de admin cargada correctamente!")
            elif "Iniciar sesión" in admin_response.text:
                print("   ❌ Aún muestra página de login - problema de autenticación")
            else:
                print("   ❓ Contenido desconocido")
                print(f"   Primeras 200 chars: {admin_response.text[:200]}...")
            
            # Paso 3: Probar /admin con cookie
            print("\n🍪 Paso 3: Probando /admin con cookie...")
            
            # Crear sesión y establecer cookie
            session = requests.Session()
            session.cookies.set("access_token", token)
            
            admin_response_cookie = session.get(f"{BASE_URL}/admin", timeout=10)
            print(f"   Admin Status (cookie): {admin_response_cookie.status_code}")
            
            if "SQL App Studio" in admin_response_cookie.text:
                print("   ✅ Página de admin cargada con cookie!")
            elif "Iniciar sesión" in admin_response_cookie.text:
                print("   ❌ Cookie no funcionó - aún muestra login")
            else:
                print("   ❓ Contenido desconocido con cookie")
            
            # Paso 4: Comparar con admin-simple que sabemos que funciona
            print("\n🔍 Paso 4: Comparando con /admin-simple...")
            simple_response = requests.get(f"{BASE_URL}/admin-simple", headers=headers, timeout=10)
            print(f"   Admin-simple Status: {simple_response.status_code}")
            
            if simple_response.status_code == 200:
                print("   ✅ Admin-simple funciona correctamente")
            else:
                print("   ❌ Admin-simple también tiene problemas")
                
        else:
            print(f"   ❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_with_auth()
