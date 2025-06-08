#!/usr/bin/env python3
"""
Script para verificar rutas disponibles y probar diferentes endpoints de login
"""
import requests
import sys

def test_routes():
    """Prueba diferentes rutas posibles para el login"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 VERIFICANDO RUTAS DISPONIBLES")
    print("=" * 50)
    
    # Posibles rutas de login
    login_routes = [
        "/usuarios/login",
        "/login", 
        "/auth/login",
        "/api/login",
        "/user/login"
    ]
    
    session = requests.Session()
    
    print("\n📍 PROBANDO RUTAS DE LOGIN:")
    for route in login_routes:
        try:
            # Primero GET para ver si existe
            get_response = session.get(f"{base_url}{route}")
            print(f"   GET {route}: {get_response.status_code}")
            
            if get_response.status_code != 404:
                # Intentar POST si GET no da 404
                login_data = {
                    "username": "juan", 
                    "password": "123456"
                }
                post_response = session.post(f"{base_url}{route}", data=login_data)
                print(f"   POST {route}: {post_response.status_code}")
                
                if post_response.status_code == 200:
                    print(f"   ✅ ENCONTRADO: {route} responde correctamente")
                    return route
                    
        except Exception as e:
            print(f"   ❌ Error en {route}: {str(e)}")
    
    # Verificar ruta principal y documentación
    print(f"\n📋 INFORMACIÓN DEL SERVIDOR:")
    try:
        root_response = session.get(f"{base_url}/")
        print(f"   Root (/): {root_response.status_code}")
        
        docs_response = session.get(f"{base_url}/docs")
        print(f"   Docs (/docs): {docs_response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Error verificando rutas base: {str(e)}")
    
    return None

def test_admin_with_correct_route(login_route):
    """Prueba el acceso al admin con la ruta de login correcta"""
    if not login_route:
        print("❌ No se encontró ruta de login válida")
        return False
        
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    print(f"\n🔐 PROBANDO LOGIN CON RUTA: {login_route}")
    print("-" * 40)
    
    # Login
    login_data = {
        "username": "juan",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{base_url}{login_route}", data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_json = login_response.json()
            print(f"✅ Login exitoso: {login_json.get('user_info', {}).get('username', 'N/A')}")
            print(f"🍪 Token en cookies: {bool(session.cookies.get('access_token'))}")
            
            # Intentar acceso al admin
            print(f"\n🏛️ PROBANDO ACCESO AL ADMIN:")
            admin_response = session.get(f"{base_url}/admin", allow_redirects=False)
            print(f"Admin Status: {admin_response.status_code}")
            
            if admin_response.status_code == 200:
                print("✅ ÉXITO: Panel de administración accesible")
                return True
            elif admin_response.status_code in [301, 302, 307, 308]:
                redirect = admin_response.headers.get('Location', 'N/A')
                print(f"🔄 Redirección a: {redirect}")
                if "login" in redirect.lower():
                    print("❌ PROBLEMA: Aún redirige al login")
                return False
            else:
                print(f"❌ Error inesperado: {admin_response.status_code}")
                return False
        else:
            print(f"❌ Error en login: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    # Buscar ruta de login correcta
    login_route = test_routes()
    
    if login_route:
        # Probar con la ruta encontrada
        success = test_admin_with_correct_route(login_route)
    else:
        print("\n❌ No se pudo encontrar una ruta de login válida")
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 BUCLE DE LOGIN RESUELTO")
    else:
        print("⚠️  BUCLE DE LOGIN AÚN PRESENTE")
    
    return success

if __name__ == "__main__":
    main()
