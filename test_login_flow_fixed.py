#!/usr/bin/env python3
"""
Script para probar el flujo completo de login y acceso a admin
"""
import requests
import json
from datetime import datetime

def test_login_admin_flow():
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 PROBANDO FLUJO COMPLETO LOGIN -> ADMIN")
    print("=" * 50)
    
    try:
        # Paso 1: Login
        print("\n1. Haciendo login...")
        login_data = {
            'username': 'juan',
            'password': 'juan123'
        }
        
        login_response = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        print(f"   Status del login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Error en login: {login_response.text}")
            return
        
        login_result = login_response.json()
        print(f"   ✅ Login exitoso")
        print(f"   Token recibido: {login_result.get('access_token', 'NO TOKEN')[:20]}...")
        
        # Paso 2: Acceder a /admin CON token
        print("\n2. Accediendo a /admin CON token...")
        token = login_result.get('access_token')
        
        if not token:
            print("   ❌ No se recibió token del login")
            return
        
        admin_response = requests.get(
            f"{base_url}/admin",
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=10
        )
        
        print(f"   Status de /admin con token: {admin_response.status_code}")
        print(f"   Headers de respuesta: {dict(admin_response.headers)}")
        
        if admin_response.status_code == 200:
            print("   ✅ Acceso exitoso a /admin")
            print(f"   Longitud del HTML: {len(admin_response.text)} caracteres")
        elif admin_response.status_code == 307:
            print(f"   🔄 Redirect 307 a: {admin_response.headers.get('location', 'No location header')}")
        elif admin_response.status_code == 401:
            print("   ❌ Token rechazado (401)")
        elif admin_response.status_code == 403:
            print("   ❌ Sin permisos (403)")
        else:
            print(f"   ❌ Error inesperado: {admin_response.status_code}")
            print(f"   Contenido: {admin_response.text[:200]}...")
        
        # Paso 3: Acceder a /admin SIN token (simular lo que pasa en el navegador)
        print("\n3. Accediendo a /admin SIN token (simulando problema)...")
        
        admin_no_token_response = requests.get(
            f"{base_url}/admin",
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=10
        )
        
        print(f"   Status de /admin sin token: {admin_no_token_response.status_code}")
        
        if admin_no_token_response.status_code == 307:
            redirect_location = admin_no_token_response.headers.get('location', 'No location')
            print(f"   🔄 Redirect a: {redirect_location}")
            print("   ✅ Esto confirma que sin token se redirige al login")
        
        # Paso 4: Probar endpoint de usuario actual
        print("\n4. Probando /usuarios/current con token...")
        
        current_user_response = requests.get(
            f"{base_url}/usuarios/current",
            headers={
                'Authorization': f'Bearer {token}'
            },
            timeout=10
        )
        
        print(f"   Status de /usuarios/current: {current_user_response.status_code}")
        
        if current_user_response.status_code == 200:
            user_data = current_user_response.json()
            print(f"   ✅ Usuario actual: {user_data.get('usuario', 'No user')}")
            print(f"   Autenticado: {user_data.get('autenticado', False)}")
            print(f"   Roles: {[r.get('nombre', 'No name') for r in user_data.get('roles', [])]}")
        else:
            print(f"   ❌ Error: {current_user_response.text}")
        
        print("\n" + "=" * 50)
        print("RESUMEN:")
        print(f"  Login: {'✅' if login_response.status_code == 200 else '❌'}")
        print(f"  Admin con token: {'✅' if admin_response.status_code == 200 else '❌'}")
        print(f"  Admin sin token: {'✅ (redirige)' if admin_no_token_response.status_code == 307 else '❌'}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_admin_flow()
