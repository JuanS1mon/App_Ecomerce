#!/usr/bin/env python3
"""
Test final del endpoint de login con datos válidos
"""

import requests
import json

def test_login_with_valid_data():
    """Prueba el login con datos válidos"""
    base_url = "http://localhost:8000"
    
    print("🔐 PROBANDO LOGIN CON DATOS VÁLIDOS")
    print("=" * 50)
    
    # Test 1: Intentar login con datos de formulario (OAuth2PasswordRequestForm)
    print("\n1. PROBANDO CON DATOS DE FORMULARIO (OAuth2PasswordRequestForm):")
    
    # Datos de formulario para OAuth2PasswordRequestForm
    form_data = {
        'username': 'admin',  # Usuario común
        'password': 'admin123',  # Contraseña común
        'grant_type': 'password'  # Requerido por OAuth2
    }
    
    try:
        # Content-Type application/x-www-form-urlencoded para OAuth2PasswordRequestForm
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(f"{base_url}/login", data=form_data, headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ LOGIN EXITOSO!")
            try:
                token_data = response.json()
                print(f"Token recibido: {token_data}")
            except:
                print("Respuesta no es JSON válido")
        else:
            print(f"❌ Error de login: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalles del error: {error_data}")
            except:
                print(f"Respuesta de error: {response.text}")
                
    except Exception as e:
        print(f"Error en la petición: {e}")
    
    # Test 2: Probar con otros usuarios comunes
    print("\n2. PROBANDO CON OTROS USUARIOS COMUNES:")
    
    common_users = [
        {'username': 'test', 'password': 'test'},
        {'username': 'user', 'password': 'password'},
        {'username': 'admin', 'password': 'password'},
        {'username': 'demo', 'password': 'demo'},
    ]
    
    for user_data in common_users:
        form_data = {
            'username': user_data['username'],
            'password': user_data['password'],
            'grant_type': 'password'
        }
        
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(f"{base_url}/login", data=form_data, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Usuario {user_data['username']}: LOGIN EXITOSO")
                break
            else:
                print(f"❌ Usuario {user_data['username']}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Usuario {user_data['username']}: Error {e}")
    
    # Test 3: Verificar que el endpoint está funcionando correctamente
    print("\n3. CONFIRMACIÓN DE FUNCIONAMIENTO:")
    
    # Enviar datos inválidos para confirmar validación
    invalid_data = {
        'username': '',  # Usuario vacío
        'password': '',  # Contraseña vacía
        'grant_type': 'password'
    }
    
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(f"{base_url}/login", data=invalid_data, headers=headers, timeout=5)
        
        print(f"Datos inválidos - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Validación funcionando correctamente (rechaza datos vacíos)")
        elif response.status_code == 422:
            print("✅ Validación funcionando correctamente (error de validación)")
        else:
            print(f"Status inesperado: {response.status_code}")
            
        try:
            error_response = response.json()
            print(f"Mensaje de error: {error_response}")
        except:
            print(f"Respuesta de error: {response.text}")
            
    except Exception as e:
        print(f"Error al probar datos inválidos: {e}")

def test_endpoint_accessibility():
    """Verifica que el endpoint es accesible"""
    base_url = "http://localhost:8000"
    
    print("\n\n🌐 VERIFICANDO ACCESIBILIDAD DEL ENDPOINT")
    print("=" * 50)
    
    try:
        # OPTIONS para verificar métodos permitidos
        response = requests.options(f"{base_url}/login", timeout=5)
        print(f"OPTIONS /login: Status {response.status_code}")
        print(f"Allow header: {response.headers.get('Allow', 'No header')}")
        
        # POST sin datos para verificar respuesta
        response = requests.post(f"{base_url}/login", timeout=5)
        print(f"POST /login (sin datos): Status {response.status_code}")
        
        if response.status_code in [400, 422]:
            print("✅ Endpoint accesible y funcionando (rechaza peticiones sin datos)")
        elif response.status_code == 405:
            print("❌ Endpoint devuelve Method Not Allowed")
        else:
            print(f"Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"Error al verificar accesibilidad: {e}")

if __name__ == "__main__":
    try:
        test_login_with_valid_data()
        test_endpoint_accessibility()
        
        print("\n\n📊 RESUMEN:")
        print("=" * 50)
        print("Si algún login fue exitoso, el problema está RESUELTO ✅")
        print("Si todos fallan pero el endpoint acepta POST, necesitas credenciales válidas")
        print("Si sigue dando 405, el problema persiste ❌")
        
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError general: {e}")
        import traceback
        traceback.print_exc()
