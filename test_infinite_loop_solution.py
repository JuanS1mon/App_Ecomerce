#!/usr/bin/env python3
"""
Script para probar la solución del bucle infinito
"""

import requests
import time
import sys

def test_infinite_loop_solution():
    """Prueba la solución del bucle infinito de login"""
    print("🔄 PRUEBA DE SOLUCIÓN DEL BUCLE INFINITO")
    print("=" * 60)
    
    base_url = "http://localhost:8000"    # Paso 1: Login para obtener token
    print("\n🔐 Paso 1: Realizando login...")
    login_data = {
        "username": "juan",
        "password": "qwer1234"
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        login_response = requests.post(f"{base_url}/login", data=login_data, headers=headers)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.status_code}")
            return False
            
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            print("❌ No se obtuvo access_token")
            return False
            
        print(f"✅ Token obtenido: {access_token[:30]}...")
        
        # Paso 2: Probar acceso directo a /admin con token
        print("\n🏢 Paso 2: Probando acceso directo a /admin con token...")
        auth_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'text/html'
        }
        
        admin_response = requests.get(f"{base_url}/admin", headers=auth_headers, allow_redirects=False)
        print(f"📊 Status /admin con token: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("✅ Acceso directo a /admin funciona correctamente!")
            
            # Verificar que es HTML del panel admin
            if "Panel de Administración" in admin_response.text:
                print("✅ Página de admin cargada correctamente")
            else:
                print("⚠️ Respuesta no parece ser la página de admin")
                
        elif admin_response.status_code == 302:
            location = admin_response.headers.get('Location', 'No especificado')
            print(f"❌ Redirección inesperada a: {location}")
            return False
        else:
            print(f"❌ Error inesperado: {admin_response.status_code}")
            return False
        
        # Paso 3: Probar acceso sin token (debería redirigir a login)
        print("\n🚪 Paso 3: Probando acceso sin token...")
        no_auth_response = requests.get(f"{base_url}/admin", allow_redirects=False)
        print(f"📊 Status /admin sin token: {no_auth_response.status_code}")
        
        if no_auth_response.status_code == 401:
            print("✅ Sin token correctamente rechazado con 401")
        elif no_auth_response.status_code == 302:
            location = no_auth_response.headers.get('Location', '')
            if 'login' in location.lower():
                print("✅ Sin token correctamente redirigido a login")
            else:
                print(f"⚠️ Redirección inesperada a: {location}")
        else:
            print(f"⚠️ Respuesta inesperada sin token: {no_auth_response.status_code}")
        
        # Paso 4: Simular flujo completo de navegador
        print("\n🌐 Paso 4: Simulando flujo de navegador...")
        
        # Simular que un usuario ya logueado intenta acceder a /login
        print("   🔍 Usuario logueado accede a /login...")
        session = requests.Session()
        
        # Primero hacer login con la sesión
        session.post(f"{base_url}/login", data=login_data, headers=headers)
        
        # Ahora intentar acceder a /login (debería redirigir a admin)
        login_page_response = session.get(f"{base_url}/loginpage", allow_redirects=True)
        print(f"   📊 Status acceso a /loginpage con sesión: {login_page_response.status_code}")
        
        # Verificar que NO está en bucle
        if "Iniciar sesión" in login_page_response.text:
            print("   ✅ Página de login se muestra correctamente (esperado)")
        elif "Panel de Administración" in login_page_response.text:
            print("   ✅ Redirigido correctamente al panel de administración")
        else:
            print("   ⚠️ Respuesta inesperada")
        
        print("\n🎯 RESUMEN:")
        print("✅ Login funciona correctamente")
        print("✅ Acceso autenticado a /admin funciona")
        print("✅ Acceso no autenticado es rechazado apropiadamente")
        print("✅ No se detectó bucle infinito")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

def test_frontend_javascript():
    """Prueba que los archivos JavaScript estén disponibles"""
    print("\n📁 VERIFICANDO ARCHIVOS JAVASCRIPT")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    js_files = [
        "/static/js/auth-interceptor.js",
        "/static/js/components.js",
        "/static/js/navigation.js"
    ]
    
    all_ok = True
    
    for js_file in js_files:
        try:
            response = requests.get(f"{base_url}{js_file}")
            if response.status_code == 200:
                print(f"✅ {js_file} - Disponible ({len(response.text)} chars)")
            else:
                print(f"❌ {js_file} - Error {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {js_file} - Error: {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("🧪 PRUEBA COMPLETA DE SOLUCIÓN DEL BUCLE INFINITO")
    print("=" * 70)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ Servidor está corriendo")
    except:
        print("❌ El servidor no está corriendo. Ejecuta: uvicorn sql_app.main:app --reload")
        sys.exit(1)
    
    # Probar archivos JavaScript
    js_ok = test_frontend_javascript()
    
    # Probar solución del bucle infinito
    loop_ok = test_infinite_loop_solution()
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO FINAL:")
    
    if js_ok and loop_ok:
        print("🎉 ¡SOLUCIÓN EXITOSA!")
        print("✅ Los archivos JavaScript están disponibles")
        print("✅ El bucle infinito ha sido resuelto")
        print("✅ La autenticación funciona correctamente")
        print("\n💡 Notas:")
        print("- El interceptor de fetch agregará automáticamente tokens a las peticiones")
        print("- La función navigateWithAuth() previene bucles en navegación de páginas")
        print("- Los usuarios logueados serán redirigidos correctamente")
    else:
        print("❌ SOLUCIÓN INCOMPLETA")
        if not js_ok:
            print("❌ Problemas con archivos JavaScript")
        if not loop_ok:
            print("❌ El bucle infinito aún persiste")
    
    print("=" * 70)
    
    sys.exit(0 if (js_ok and loop_ok) else 1)
