#!/usr/bin/env python3
"""
Script para probar si el bucle de login en el panel de administración se ha solucionado
"""
import requests
import sys

def test_admin_access():
    """Prueba el acceso al panel de administración después de las correcciones"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔧 PRUEBA POST-CORRECCIÓN: Acceso al Panel de Administración")
    print("=" * 60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Login
    print("\n1️⃣ INICIANDO SESIÓN...")
    login_data = {
        "username": "juan",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{base_url}/usuarios/login", data=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_json = login_response.json()
            print(f"   ✅ Login exitoso para: {login_json.get('user_info', {}).get('username', 'N/A')}")
            print(f"   🍪 Cookies establecidas: {bool(session.cookies.get('access_token'))}")
        else:
            print(f"   ❌ Error en login: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {str(e)}")
        return False
    
    # 2. Acceso directo al admin (GET)
    print("\n2️⃣ ACCEDIENDO AL PANEL DE ADMINISTRACIÓN...")
    try:
        admin_response = session.get(f"{base_url}/admin", allow_redirects=False)
        print(f"   Status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("   ✅ ÉXITO: Acceso directo al panel de administración")
            if "<!DOCTYPE html>" in admin_response.text:
                print("   📄 Respuesta contiene HTML válido")
            return True
        elif admin_response.status_code in [301, 302, 307, 308]:
            redirect_location = admin_response.headers.get('Location', 'N/A')
            print(f"   🔄 Redirección a: {redirect_location}")
            
            if "login" in redirect_location.lower():
                print("   ❌ PROBLEMA: Aún redirige al login (bucle no resuelto)")
                return False
            else:
                print("   ⚠️  Redirección a ubicación diferente")
                return False
        else:
            print(f"   ❌ Error inesperado: {admin_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al acceder al admin: {str(e)}")
        return False

    # 3. Seguir redirecciones automáticamente para comparar
    print("\n3️⃣ SIGUIENDO REDIRECCIONES AUTOMÁTICAS...")
    try:
        admin_follow = session.get(f"{base_url}/admin", allow_redirects=True)
        print(f"   Status final: {admin_follow.status_code}")
        print(f"   URL final: {admin_follow.url}")
        
        if "loginpage" in admin_follow.url:
            print("   ❌ CONFIRMADO: Termina en página de login (bucle activo)")
        elif "admin" in admin_follow.url:
            print("   ✅ CONFIRMADO: Se mantiene en admin (bucle resuelto)")
        else:
            print(f"   ⚠️  Termina en ubicación inesperada: {admin_follow.url}")
            
    except Exception as e:
        print(f"   ⚠️  Error siguiendo redirecciones: {str(e)}")

def main():
    success = test_admin_access()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULTADO: BUCLE DE LOGIN RESUELTO")
        print("✅ El panel de administración es accesible después del login")
    else:
        print("⚠️  RESULTADO: PROBLEMA AÚN PRESENTE")
        print("❌ Se requiere investigación adicional")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    main()
