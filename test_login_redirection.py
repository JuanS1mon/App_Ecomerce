#!/usr/bin/env python3
"""
Script para probar específicamente el problema de redirección después del login
"""
import requests
import json

def test_login_redirection():
    """Prueba el flujo de login y redirección"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 PROBANDO FLUJO DE LOGIN Y REDIRECCIÓN")
    print("=" * 50)
    
    try:
        # Paso 1: Hacer login
        print("\n1. Realizando login...")
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
            return False
        
        login_result = login_response.json()
        print(f"   ✅ Login exitoso")
        print(f"   Token recibido: {login_result.get('access_token', 'NO TOKEN')[:20]}...")
        
        # Paso 2: Verificar que el token funciona accediendo a /admin
        print("\n2. Verificando acceso a /admin con token...")
        token = login_result.get('access_token')
        
        if not token:
            print("   ❌ No se recibió token del login")
            return False
        
        admin_response = requests.get(
            f"{base_url}/admin",
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=10
        )
        
        print(f"   Status de /admin con token: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("   ✅ Acceso exitoso a /admin con token")
            print("   ✅ El backend funciona correctamente")
            return True
        elif admin_response.status_code == 401:
            print("   ❌ Token rechazado por /admin")
            return False
        else:
            print(f"   ⚠️ Respuesta inesperada de /admin: {admin_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_login_page_access():
    """Prueba el acceso a la página de login"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔍 PROBANDO ACCESO A PÁGINA DE LOGIN")
    print("=" * 40)
    
    try:
        # Verificar que podemos acceder a la página de login
        login_page_response = requests.get(f"{base_url}/loginpage", timeout=10)
        print(f"   Status de /loginpage: {login_page_response.status_code}")
        
        if login_page_response.status_code == 200:
            print("   ✅ Página de login accesible")
            return True
        else:
            print(f"   ❌ Error accediendo a página de login")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO DEL PROBLEMA DE REDIRECCIÓN")
    print("=" * 55)
    
    # Verificar acceso a la página de login
    login_page_ok = test_login_page_access()
    
    # Verificar el flujo de login
    login_flow_ok = test_login_redirection()
    
    print("\n" + "=" * 55)
    print("📊 RESULTADOS:")
    print(f"   Página de login accesible: {'✅ SÍ' if login_page_ok else '❌ NO'}")
    print(f"   Flujo de login funcional: {'✅ SÍ' if login_flow_ok else '❌ NO'}")
    
    if login_page_ok and login_flow_ok:
        print("\n🎉 ¡EL BACKEND FUNCIONA CORRECTAMENTE!")
        print("💡 El problema debe estar en el JavaScript del frontend")
        print("📋 Revisar el archivo login.html para encontrar el problema de redirección")
    else:
        print("\n⚠️ Hay problemas en el backend que deben resolverse primero")
