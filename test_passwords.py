#!/usr/bin/env python3
"""
Script para probar diferentes contraseñas para testuser
"""

import requests
import json

def test_different_passwords():
    """Probar diferentes contraseñas para testuser"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🔧 PROBANDO DIFERENTES CONTRASEÑAS PARA TESTUSER")
    print("=" * 60)
    
    # Lista de contraseñas comunes que podrían estar configuradas
    passwords_to_test = [
        "testpass123",
        "testpassword",
        "test123",
        "123456",
        "password",
        "admin",
        "admin123",
        "testuser",
        "password123",
        "test",
        "12345678"
    ]
    
    username = "testuser"
    
    for password in passwords_to_test:
        try:
            print(f"\n🔑 Probando: {username} / {password}")
            
            login_data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(
                f"{BASE_URL}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
                allow_redirects=False  # No seguir redirecciones automáticamente
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ ¡LOGIN EXITOSO!")
                try:
                    result = response.json()
                    if "access_token" in result:
                        print(f"   🎟️ Token: {result['access_token'][:50]}...")
                        return username, password, result['access_token']
                    else:
                        print(f"   📄 Respuesta: {result}")
                except:
                    print(f"   📄 Respuesta (no JSON): {response.text[:200]}...")
                    
            elif response.status_code == 307:
                print(f"   🔄 Redirección a: {response.headers.get('location', 'N/A')}")
                
            elif response.status_code == 401:
                print("   ❌ Credenciales incorrectas")
                
            elif response.status_code == 405:
                print("   ❌ Método no permitido")
                
            else:
                print(f"   ❓ Código inesperado: {response.status_code}")
                print(f"   📄 Respuesta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ Ninguna contraseña funcionó")
    return None, None, None

def test_registration():
    """Intentar registrar un nuevo usuario de prueba"""
    
    BASE_URL = "http://localhost:8000"
    
    print("\n🆕 INTENTANDO REGISTRAR NUEVO USUARIO")
    print("=" * 50)
    
    try:
        # Datos para registrar nuevo usuario
        register_data = {
            "usuario": "newtest",
            "clave": "newtest123",
            "mail": "newtest@example.com",
            "nombre": "New Test User"
        }
        
        # Probar endpoint de registro
        register_response = requests.post(
            f"{BASE_URL}/registro",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Registro Status: {register_response.status_code}")
        
        if register_response.status_code in [200, 201]:
            print("✅ Usuario registrado correctamente")
            
            # Intentar login con el nuevo usuario
            login_data = {
                "username": "newtest",
                "password": "newtest123"
            }
            
            login_response = requests.post(
                f"{BASE_URL}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
                allow_redirects=False
            )
            
            print(f"Login con nuevo usuario Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print("✅ Login con nuevo usuario exitoso!")
                try:
                    result = login_response.json()
                    if "access_token" in result:
                        return "newtest", "newtest123", result['access_token']
                except:
                    pass
        else:
            print(f"❌ Error en registro: {register_response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error en registro: {e}")
    
    return None, None, None

if __name__ == "__main__":
    # Probar contraseñas existentes
    username, password, token = test_different_passwords()
    
    if not token:
        # Intentar registrar nuevo usuario
        username, password, token = test_registration()
    
    if token:
        print(f"\n🎉 CREDENCIALES FUNCIONANDO:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"\n❌ No se pudieron obtener credenciales válidas")
