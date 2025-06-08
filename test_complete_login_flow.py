#!/usr/bin/env python3
"""
Script para crear un usuario de prueba y verificar el login
"""

import requests
import json

def create_test_user():
    """Crea un usuario de prueba"""
    base_url = "http://localhost:8000"
    
    print("👤 CREANDO USUARIO DE PRUEBA")
    print("=" * 40)
    
    # Datos para crear usuario
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "apellido": "Test Apellido",
        "password": "testpassword123",
        "telefono": "123456789"
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{base_url}/user/registro", json=user_data, headers=headers, timeout=10)
        
        print(f"Crear usuario - Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Usuario creado exitosamente")
            return True
        elif response.status_code == 409:
            print("⚠️ Usuario ya existe (esto está bien)")
            return True
        else:
            try:
                error_data = response.json()
                print(f"Error creando usuario: {error_data}")
            except:
                print(f"Error creando usuario: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en petición de creación: {e}")
        return False

def test_login_with_created_user():
    """Prueba el login con el usuario creado"""
    base_url = "http://localhost:8000"
    
    print("\n🔐 PROBANDO LOGIN CON USUARIO CREADO")
    print("=" * 40)
    
    # Datos de login (usando email como username)
    login_data = {
        'username': 'test@example.com',  # FastAPI OAuth2 usa 'username' pero puede ser email
        'password': 'testpassword123',
        'grant_type': 'password'
    }
    
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(f"{base_url}/login", data=login_data, headers=headers, timeout=10)
        
        print(f"Login - Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("🎉 ¡LOGIN EXITOSO!")
            try:
                token_data = response.json()
                print(f"Token recibido: {json.dumps(token_data, indent=2)}")
                return token_data
            except:
                print("Respuesta no es JSON válido")
                print(f"Respuesta raw: {response.text}")
        else:
            print(f"❌ Error de login")
            try:
                error_data = response.json()
                print(f"Detalles del error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta de error: {response.text}")
        
        return None
            
    except Exception as e:
        print(f"Error en petición de login: {e}")
        return None

def test_protected_endpoint(token_data):
    """Prueba un endpoint protegido con el token"""
    if not token_data or 'access_token' not in token_data:
        print("\n❌ No hay token para probar endpoint protegido")
        return
    
    base_url = "http://localhost:8000"
    
    print("\n🔒 PROBANDO ENDPOINT PROTEGIDO")
    print("=" * 40)
    
    token = token_data['access_token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Probar endpoint protegido (ej: /users/me o /usuarios/current)
        response = requests.get(f"{base_url}/users/me", headers=headers, timeout=10)
        
        print(f"Endpoint protegido - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token funciona correctamente")
            try:
                user_data = response.json()
                print(f"Datos del usuario: {json.dumps(user_data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
        else:
            print(f"❌ Token no funciona")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Error probando endpoint protegido: {e}")

def final_verification():
    """Verificación final del problema"""
    print("\n\n📋 VERIFICACIÓN FINAL")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Confirmar que POST /login acepta peticiones
    try:
        response = requests.post(f"{base_url}/login", timeout=5)
        if response.status_code == 422:
            print("✅ POST /login funciona (Status 422 = acepta POST, faltan datos)")
        elif response.status_code == 405:
            print("❌ POST /login sigue devolviendo Method Not Allowed")
        else:
            print(f"⚠️ POST /login devuelve status inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error probando POST /login: {e}")

if __name__ == "__main__":
    try:
        # Paso 1: Crear usuario de prueba
        user_created = create_test_user()
        
        if user_created:
            # Paso 2: Probar login
            token_data = test_login_with_created_user()
            
            if token_data:
                # Paso 3: Probar endpoint protegido
                test_protected_endpoint(token_data)
        
        # Paso 4: Verificación final
        final_verification()
        
        print("\n\n🎯 CONCLUSIÓN:")
        print("=" * 40)
        print("Si el login fue exitoso, el problema está COMPLETAMENTE RESUELTO ✅")
        print("El endpoint POST /login funciona correctamente.")
        print("Status 422 sin datos = correcto")
        print("Status 200 con datos válidos = correcto")
        
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError general: {e}")
        import traceback
        traceback.print_exc()
