#!/usr/bin/env python3
"""
Script para probar el login directo y el panel de administración
"""
import requests
import sys

def test_direct_login():
    """Prueba el login directo sin prefijo"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔐 PRUEBA DIRECTA DE LOGIN Y ACCESO AL ADMIN")
    print("=" * 55)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Login usando OAuth2PasswordRequestForm
    print("\n1️⃣ PROBANDO LOGIN (OAuth2PasswordRequestForm)...")
    login_data = {
        "username": "juan",
        "password": "123456"
    }
    
    try:
        # El endpoint esperará form data, no JSON
        login_response = session.post(
            f"{base_url}/login", 
            data=login_data,  # Usar data en lugar de json
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            print(f"   ✅ Login exitoso")
            print(f"   👤 Usuario: {response_data.get('user_info', {}).get('username', 'N/A')}")
            print(f"   🍪 Cookie token: {bool(session.cookies.get('access_token'))}")
            
            # Verificar headers de respuesta para cookies
            cookies_in_header = login_response.headers.get('set-cookie', '')
            print(f"   📋 Set-Cookie header: {'Presente' if 'access_token' in cookies_in_header else 'No encontrado'}")
            
        elif login_response.status_code == 422:
            print(f"   ❌ Error de validación: {login_response.text}")
            return False
        else:
            print(f"   ❌ Error en login: {login_response.status_code} - {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {str(e)}")
        return False
    
    # 2. Acceso al panel de administración
    print(f"\n2️⃣ PROBANDO ACCESO AL ADMIN...")
    try:
        # Mostrar cookies actuales
        current_cookies = dict(session.cookies)
        print(f"   🍪 Cookies disponibles: {list(current_cookies.keys())}")
        
        admin_response = session.get(f"{base_url}/admin", allow_redirects=False)
        print(f"   Status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("   ✅ ÉXITO: Panel de administración accesible directamente")
            print("   🎉 BUCLE DE LOGIN RESUELTO")
            return True
            
        elif admin_response.status_code in [301, 302, 307, 308]:
            redirect_location = admin_response.headers.get('Location', 'N/A')
            print(f"   🔄 Redirección a: {redirect_location}")
            
            if "login" in redirect_location.lower():
                print("   ❌ PROBLEMA: Aún redirige al login")
                
                # Seguir la redirección para ver el comportamiento completo
                print(f"\n3️⃣ SIGUIENDO REDIRECCIÓN...")
                final_response = session.get(f"{base_url}/admin", allow_redirects=True)
                print(f"   Status final: {final_response.status_code}")
                print(f"   URL final: {final_response.url}")
                
                return False
            else:
                print(f"   ⚠️  Redirección a ubicación inesperada: {redirect_location}")
                return False
                
        elif admin_response.status_code == 401:
            print("   ❌ No autorizado - problema de autenticación")
            return False
        elif admin_response.status_code == 403:
            print("   ❌ Prohibido - usuario no tiene permisos de admin")
            return False
        else:
            print(f"   ❌ Error inesperado: {admin_response.status_code}")
            print(f"   📄 Respuesta: {admin_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al acceder al admin: {str(e)}")
        return False

def main():
    success = test_direct_login()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 RESULTADO: BUCLE DE LOGIN RESUELTO CON ÉXITO")
        print("✅ Las correcciones de importación funcionaron")
    else:
        print("⚠️  RESULTADO: BUCLE DE LOGIN AÚN PRESENTE")
        print("🔧 Se requiere depuración adicional")
    
    print("=" * 55)
    return success

if __name__ == "__main__":
    main()
