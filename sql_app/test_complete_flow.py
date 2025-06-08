#!/usr/bin/env python3
"""
Script para probar el flujo completo de login y redirección
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8001"

def test_complete_login_flow():
    """Prueba el flujo completo de login y acceso a admin"""
    
    print("🧪 PRUEBA DE FLUJO COMPLETO DE LOGIN")
    print("=" * 50)
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    # 1. Probar login
    print("1️⃣ Probando login...")
    
    login_url = urljoin(BASE_URL, "/login")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = session.post(login_url, data=login_data)
    
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Error en login: {login_response.text}")
        return False
    
    try:
        login_json = login_response.json()
        token = login_json.get('access_token')
        print(f"   ✅ Login exitoso, token recibido: {token[:20]}...")
        
        # Verificar que se estableció la cookie
        cookies = session.cookies.get_dict()
        print(f"   🍪 Cookies establecidas: {list(cookies.keys())}")
        
    except Exception as e:
        print(f"   ❌ Error procesando respuesta de login: {e}")
        return False
    
    # 2. Probar acceso a admin sin token en header (solo cookies)
    print("\n2️⃣ Probando acceso a /admin con cookies...")
    
    admin_url = urljoin(BASE_URL, "/admin")
    admin_response = session.get(admin_url)
    
    print(f"   Status: {admin_response.status_code}")
    
    if admin_response.status_code == 200:
        print("   ✅ Acceso exitoso a /admin con cookies")
        if "admin" in admin_response.text.lower() or "panel" in admin_response.text.lower():
            print("   ✅ Página de admin cargada correctamente")
        else:
            print("   ⚠️ Respuesta no parece ser página de admin")
    else:
        print(f"   ❌ Error accediendo a admin: {admin_response.status_code}")
        print(f"   Respuesta: {admin_response.text[:200]}...")
    
    # 3. Probar acceso con token en header
    print("\n3️⃣ Probando acceso a /admin con token en header...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    admin_response_with_token = session.get(admin_url, headers=headers)
    
    print(f"   Status: {admin_response_with_token.status_code}")
    
    if admin_response_with_token.status_code == 200:
        print("   ✅ Acceso exitoso a /admin con token")
    else:
        print(f"   ❌ Error accediendo a admin con token: {admin_response_with_token.status_code}")
    
    # 4. Probar otras rutas relacionadas
    print("\n4️⃣ Probando otras rutas...")
    
    routes_to_test = ["/admin/", "/admin/perfil", "/usuarios_admin/"]
    
    for route in routes_to_test:
        url = urljoin(BASE_URL, route)
        response = session.get(url, headers=headers)
        print(f"   {route}: {response.status_code}")
    
    return True

def test_browser_simulation():
    """Simula lo que haría un navegador"""
    
    print("\n🌐 SIMULACIÓN DE NAVEGADOR")
    print("=" * 30)
    
    # Simular el proceso completo como lo haría un navegador
    session = requests.Session()
    
    # 1. Cargar página de login
    login_page_url = urljoin(BASE_URL, "/loginpage")
    print(f"1️⃣ Cargando página de login: {login_page_url}")
    
    login_page_response = session.get(login_page_url)
    print(f"   Status: {login_page_response.status_code}")
    
    if login_page_response.status_code != 200:
        print("   ❌ Error cargando página de login")
        return
    
    # 2. Enviar formulario de login
    print("2️⃣ Enviando formulario de login...")
    
    login_url = urljoin(BASE_URL, "/login")
    form_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": login_page_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    login_response = session.post(login_url, data=form_data, headers=headers)
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        # 3. Seguir redirección a admin
        print("3️⃣ Siguiendo redirección a admin...")
        
        admin_url = urljoin(BASE_URL, "/admin")
        admin_response = session.get(admin_url)
        
        print(f"   Status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("   ✅ Redirección exitosa a admin")
            return True
        else:
            print(f"   ❌ Error en redirección: {admin_response.text[:200]}")
    
    return False

if __name__ == "__main__":
    try:
        # Probar flujo completo
        success1 = test_complete_login_flow()
        
        # Probar simulación de navegador
        success2 = test_browser_simulation()
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Flujo completo: {'✅ Exitoso' if success1 else '❌ Falló'}")
        print(f"   Simulación navegador: {'✅ Exitoso' if success2 else '❌ Falló'}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
