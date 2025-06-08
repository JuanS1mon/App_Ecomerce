#!/usr/bin/env python3
"""
Script para diagnosticar el problema de logout - usuario sigue logeado después del logout
"""

import requests
import json

def test_logout_flow():
    """Prueba el flujo completo de logout"""
    base_url = "http://localhost:8000"
    
    print("🔒 DIAGNÓSTICO DEL PROBLEMA DE LOGOUT")
    print("=" * 50)
    
    # Test 1: Primero verificar el estado inicial sin autenticación
    print("\n1. VERIFICANDO ESTADO INICIAL (sin autenticación):")
    try:
        response = requests.get(f"{base_url}/admin", timeout=5)
        print(f"GET /admin sin auth: Status {response.status_code}")
        if response.status_code == 200:
            print("⚠️ /admin accesible sin autenticación")
        elif response.status_code in [302, 303, 307, 308]:
            print(f"✅ /admin redirige correctamente: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"✅ /admin protegido correctamente")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Intentar hacer login para obtener una sesión
    print("\n2. INTENTANDO LOGIN PARA OBTENER SESIÓN:")
    session = requests.Session()
    
    # Primero obtener la página de login para ver si hay algún redirect
    try:
        response = session.get(f"{base_url}/loginpage", timeout=5)
        print(f"GET /loginpage: Status {response.status_code}")
    except Exception as e:
        print(f"Error obteniendo loginpage: {e}")
    
    # Intentar login con datos de prueba
    login_data = {
        'username': 'testuser',  # Ajustar según los usuarios disponibles
        'password': 'testpassword123',
        'grant_type': 'password'
    }
    
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = session.post(f"{base_url}/login", data=login_data, headers=headers, timeout=10)
        print(f"POST /login: Status {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login exitoso")
            try:
                token_data = response.json()
                print(f"Token recibido: {token_data.get('token_type', 'No type')} {token_data.get('access_token', 'No token')[:20]}...")
            except:
                print("Respuesta no es JSON")
        else:
            print(f"❌ Login falló: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error en login: {e}")
    
    # Test 3: Verificar acceso a endpoint protegido CON sesión
    print("\n3. VERIFICANDO ACCESO CON SESIÓN:")
    try:
        response = session.get(f"{base_url}/admin", timeout=5)
        print(f"GET /admin con sesión: Status {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Acceso autorizado a /admin")
        elif response.status_code in [302, 303, 307, 308]:
            print(f"⚠️ Redirección con sesión: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ Acceso denegado con sesión: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Realizar logout
    print("\n4. REALIZANDO LOGOUT:")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = session.post(f"{base_url}/logout", headers=headers, timeout=10)
        print(f"POST /logout: Status {response.status_code}")
        print(f"Headers de respuesta: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                logout_data = response.json()
                print(f"Respuesta logout: {logout_data}")
            except:
                print(f"Respuesta logout (text): {response.text}")
        else:
            print(f"❌ Logout falló: {response.status_code}")
            print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"Error en logout: {e}")
    
    # Test 5: Verificar que la sesión se cerró
    print("\n5. VERIFICANDO QUE LA SESIÓN SE CERRÓ:")
    try:
        response = session.get(f"{base_url}/admin", timeout=5)
        print(f"GET /admin después del logout: Status {response.status_code}")
        
        if response.status_code == 200:
            print("❌ PROBLEMA: Todavía tiene acceso a /admin después del logout")
        elif response.status_code in [302, 303, 307, 308]:
            location = response.headers.get('Location', 'Unknown')
            print(f"✅ Redirige correctamente después del logout: {location}")
            if 'login' in location.lower():
                print("✅ Redirige al login (correcto)")
            else:
                print(f"⚠️ Redirige a: {location} (puede no ser correcto)")
        else:
            print(f"✅ Acceso denegado después del logout: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Verificar cookies después del logout
    print("\n6. VERIFICANDO COOKIES DESPUÉS DEL LOGOUT:")
    print(f"Cookies en sesión: {dict(session.cookies)}")
    
    if 'access_token' in session.cookies:
        print("❌ PROBLEMA: Cookie access_token todavía presente")
    else:
        print("✅ Cookie access_token eliminada correctamente")

def test_manual_logout():
    """Prueba manual del endpoint de logout"""
    base_url = "http://localhost:8000"
    
    print("\n\n🔧 PRUEBA MANUAL DEL ENDPOINT LOGOUT")
    print("=" * 50)
    
    # Test directo del endpoint logout
    try:
        response = requests.post(f"{base_url}/logout", timeout=5)
        print(f"POST /logout (sin auth): Status {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctamente requiere autenticación")
        elif response.status_code == 422:
            print("⚠️ Error de validación (posible problema con dependencias)")
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            
        try:
            error_data = response.json()
            print(f"Detalles: {error_data}")
        except:
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def check_redirect_behavior():
    """Verifica el comportamiento de redirección"""
    base_url = "http://localhost:8000"
    
    print("\n\n🔄 VERIFICANDO COMPORTAMIENTO DE REDIRECCIÓN")
    print("=" * 50)
    
    endpoints_to_test = [
        '/admin',
        '/usuarios/current',
        '/users/me',
    ]
    
    for endpoint in endpoints_to_test:
        try:
            # Probar sin seguir redirecciones
            response = requests.get(f"{base_url}{endpoint}", allow_redirects=False, timeout=5)
            print(f"GET {endpoint}: Status {response.status_code}")
            
            if response.status_code in [302, 303, 307, 308]:
                location = response.headers.get('Location', 'No location')
                print(f"  Redirige a: {location}")
                
                if 'login' in location.lower():
                    print("  ✅ Redirige al login (correcto)")
                else:
                    print("  ⚠️ No redirige al login")
            elif response.status_code == 401:
                print("  ✅ Devuelve 401 Unauthorized (correcto)")
            elif response.status_code == 200:
                print("  ❌ PROBLEMA: Acceso sin autenticación")
            else:
                print(f"  ⚠️ Respuesta inesperada: {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    try:
        test_logout_flow()
        test_manual_logout()
        check_redirect_behavior()
        
        print("\n\n📋 RESUMEN DEL DIAGNÓSTICO:")
        print("=" * 50)
        print("1. Verifica si el login funciona correctamente")
        print("2. Verifica si el logout elimina la cookie access_token")
        print("3. Verifica si los endpoints protegidos redirigen después del logout")
        print("4. Verifica si hay middleware que mantenga la sesión activa")
        
    except KeyboardInterrupt:
        print("\n\nDiagnóstico interrumpido por el usuario")
    except Exception as e:
        print(f"\n\nError general: {e}")
        import traceback
        traceback.print_exc()
