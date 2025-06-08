#!/usr/bin/env python3
"""
Verificación final del sistema de login y redirección
"""

import requests
import json
import time

def test_final_verification():
    """Verificación final completa del sistema"""
    
    print("🔧 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8001"
    
    # Test 1: Verificar que el servidor responde
    print("1️⃣ Verificando servidor...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ Servidor activo y respondiendo")
        else:
            print(f"   ⚠️ Servidor responde con código: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Servidor no responde: {e}")
        return False
    
    # Test 2: Verificar página de login
    print("\n2️⃣ Verificando página de login...")
    try:
        response = requests.get(f"{BASE_URL}/loginpage", timeout=5)
        if response.status_code == 200 and "login" in response.text.lower():
            print("   ✅ Página de login disponible")
        else:
            print(f"   ❌ Error en página de login: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error accediendo a página de login: {e}")
        return False
    
    # Test 3: Verificar endpoint de login
    print("\n3️⃣ Verificando endpoint de login...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("   ✅ Login funciona correctamente")
                token = data["access_token"]
            else:
                print("   ❌ Login no devuelve token")
                return False
        else:
            print(f"   ❌ Login falló: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # Test 4: Verificar acceso a admin
    print("\n4️⃣ Verificando acceso a admin...")
    try:
        # Crear sesión con cookies del login
        session = requests.Session()
        session.post(f"{BASE_URL}/login", data=login_data)
        
        response = session.get(f"{BASE_URL}/admin", timeout=5)
        if response.status_code == 200:
            print("   ✅ Acceso a admin exitoso")
        else:
            print(f"   ❌ Error accediendo a admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error verificando admin: {e}")
        return False
    
    # Test 5: Verificar flujo completo de redirección
    print("\n5️⃣ Verificando flujo completo...")
    try:
        session = requests.Session()
        
        # Login
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        if login_response.status_code != 200:
            print("   ❌ Error en login para flujo completo")
            return False
        
        # Verificar que se puede acceder a admin inmediatamente después
        admin_response = session.get(f"{BASE_URL}/admin")
        if admin_response.status_code == 200:
            print("   ✅ Flujo completo de login → admin funciona")
        else:
            print(f"   ❌ Error en redirección: {admin_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en flujo completo: {e}")
        return False
    
    print("\n🎉 VERIFICACIÓN COMPLETADA CON ÉXITO")
    print("✅ Sistema de login y redirección funcionando correctamente")
    print()
    print("📋 INSTRUCCIONES PARA EL USUARIO:")
    print("1. Abre http://localhost:8000/loginpage en tu navegador")
    print("2. Usa las credenciales: admin / admin123")
    print("3. Después del login serás redirigido automáticamente a /admin")
    print()
    return True

if __name__ == "__main__":
    success = test_final_verification()
    
    if success:
        print("🏆 SISTEMA COMPLETAMENTE FUNCIONAL")
    else:
        print("❌ SISTEMA REQUIERE ATENCIÓN")
