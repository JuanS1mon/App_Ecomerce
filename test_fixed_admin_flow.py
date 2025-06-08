#!/usr/bin/env python3
"""
Test completo del flujo de autenticación admin después de la corrección
Verifica que el endpoint /usuarios/current ahora funciona correctamente
"""

import requests
import json
from time import sleep

# Configuración del servidor
BASE_URL = "http://127.0.0.1:8001"
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

def test_complete_admin_flow():
    """
    Prueba el flujo completo:
    1. Login con credenciales admin
    2. Verificar que /usuarios/current devuelve información correcta del usuario autenticado
    3. Verificar acceso al panel admin
    """
    print("🧪 Iniciando prueba completa del flujo admin corregido...")
    
    # Paso 1: Login
    print("\n1️⃣ Realizando login con credenciales admin...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/login",
            data=login_data,
            headers=HEADERS,
            allow_redirects=False
        )
        
        print(f"   📋 Status login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            token = response_data.get("access_token")
            print(f"   ✅ Login exitoso - Token obtenido")
            print(f"   🔑 Token type: {response_data.get('token_type')}")
            
            # Paso 2: Verificar /usuarios/current con el token
            print("\n2️⃣ Probando endpoint /usuarios/current corregido...")
            auth_headers = {"Authorization": f"Bearer {token}"}
            
            current_user_response = requests.get(
                f"{BASE_URL}/usuarios/current",
                headers=auth_headers
            )
            
            print(f"   📋 Status /usuarios/current: {current_user_response.status_code}")
            
            if current_user_response.status_code == 200:
                user_data = current_user_response.json()
                print("   ✅ Endpoint /usuarios/current funciona correctamente")
                print(f"   👤 Usuario: {user_data.get('nombre', 'N/A')}")
                print(f"   📧 Email: {user_data.get('email', 'N/A')}")
                print(f"   🔐 Role: {user_data.get('role', 'N/A')}")
                print(f"   🎯 Autenticado: {user_data.get('autenticado', False)}")
                
                # Verificar que no es usuario invitado
                if user_data.get('nombre') != 'Invitado' and user_data.get('autenticado'):
                    print("   🎉 CORRECCIÓN EXITOSA: El usuario está correctamente autenticado")
                    
                    # Paso 3: Probar acceso al panel admin
                    print("\n3️⃣ Probando acceso al panel admin...")
                    admin_response = requests.get(
                        f"{BASE_URL}/admin",
                        headers=auth_headers,
                        allow_redirects=False
                    )
                    
                    print(f"   📋 Status /admin: {admin_response.status_code}")
                    
                    if admin_response.status_code == 200:
                        print("   🎊 ÉXITO TOTAL: Acceso al panel admin funcionando")
                        return True
                    elif admin_response.status_code == 302 or admin_response.status_code == 307:
                        print("   ⚠️  Redirección desde /admin - verificar lógica de roles")
                        print(f"   📍 Location: {admin_response.headers.get('location', 'N/A')}")
                    else:
                        print(f"   ❌ Error accediendo a /admin: {admin_response.text[:200]}")
                else:
                    print("   ❌ PROBLEMA: Aún devuelve usuario invitado o no autenticado")
                    
            else:
                print(f"   ❌ Error en /usuarios/current: {current_user_response.text[:200]}")
                
        elif login_response.status_code in [302, 307]:
            print(f"   ❌ Login falló - Redirección: {login_response.headers.get('location', 'N/A')}")
        else:
            print(f"   ❌ Error en login: {login_response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al servidor en puerto 8001")
        print("   💡 Asegúrate de que el servidor esté ejecutándose con: python -m sql_app.main")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
        return False
    
    return False

def check_server_status():
    """Verifica si el servidor está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔧 Test del flujo admin después de la corrección crítica")
    print("=" * 60)
    
    # Verificar servidor
    if not check_server_status():
        print("❌ Servidor no disponible en puerto 8001")
        print("💡 Ejecuta: python -m sql_app.main")
        exit(1)
    
    # Ejecutar prueba
    success = test_complete_admin_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODAS LAS PRUEBAS PASARON - El problema está RESUELTO")
    else:
        print("⚠️  Algunas pruebas fallaron - Revisar logs para más detalles")
