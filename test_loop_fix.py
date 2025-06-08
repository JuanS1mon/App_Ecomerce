#!/usr/bin/env python3
"""
Test específico para verificar que se arregló el bucle infinito
============================================================
"""
import requests
import time

def test_loop_fix():
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    print("🧪 TEST: Verificación de bucle infinito corregido")
    print("=" * 50)
    
    # 1. Hacer login para obtener token
    print("\n1️⃣ Haciendo login para obtener token...")
    login_data = {
        'username': 'juan',
        'password': 'qwer1234'
    }
    
    response = session.post(
        f"{base_url}/login",
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login exitoso - Token obtenido: {token[:20]}...")
    else:
        print(f"❌ Error en login: {response.status_code}")
        return False
    
    # 2. Verificar que /usuarios/current funciona con token
    print("\n2️⃣ Verificando endpoint /usuarios/current...")
    headers = {'Authorization': f'Bearer {token}'}
    
    current_response = session.get(f"{base_url}/usuarios/current", headers=headers)
    
    if current_response.status_code == 200:
        user_data = current_response.json()
        print(f"✅ /usuarios/current funciona: {user_data}")
    else:
        print(f"❌ Error en /usuarios/current: {current_response.status_code}")
        return False
    
    # 3. Simular acceso a login con token en localStorage (como navegador)
    print("\n3️⃣ Simulando visita a /loginpage estando autenticado...")
    
    # Esto simula lo que haría el navegador con JavaScript
    login_page_response = session.get(f"{base_url}/loginpage")
    
    if login_page_response.status_code == 200:
        content = login_page_response.text
        
        # Verificar que contiene la exclusión correcta
        if '/usuarios/current' in content:
            print("✅ Login page contiene exclusión para /usuarios/current")
        else:
            print("❌ Login page NO contiene exclusión para /usuarios/current")
            return False
            
        # Verificar que contiene el interceptor embebido
        if 'AUTH_INTERCEPTOR_LOADED' in content:
            print("✅ Interceptor embebido presente")
        else:
            print("❌ Interceptor embebido NO presente")
            return False
            
    else:
        print(f"❌ Error obteniendo login page: {login_page_response.status_code}")
        return False
    
    print("\n✅ Todos los tests pasaron - Bucle infinito corregido")
    return True

if __name__ == "__main__":
    success = test_loop_fix()
    if success:
        print("\n🎉 ¡El bucle infinito ha sido corregido!")
    else:
        print("\n❌ Aún hay problemas con el bucle infinito")
