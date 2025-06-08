#!/usr/bin/env python3
"""
Test directo usando requests para verificar exactamente qué está pasando
"""

import requests
import json

def test_network_behavior():
    """Analizar el comportamiento de red paso a paso"""
    
    print("🔍 ANÁLISIS DETALLADO DE COMPORTAMIENTO DE RED")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # Paso 1: Simular que el usuario abre la página de login
    print("📄 PASO 1: Accediendo a la página de login original...")
    try:
        login_page = session.get(f"{base_url}/loginpage", allow_redirects=True)
        print(f"Status: {login_page.status_code}")
        print(f"URL final: {login_page.url}")
        print(f"Cookies recibidas: {dict(session.cookies)}")
        
        # Verificar si hay algún token o sesión previa
        if 'access_token' in session.cookies:
            print(f"⚠️  Token previo encontrado: {session.cookies['access_token'][:30]}...")
        
    except Exception as e:
        print(f"❌ Error accediendo a loginpage: {e}")
        return
    
    print(f"\n" + "="*40)
    
    # Paso 2: Hacer login con las credenciales de prueba
    print("🔐 PASO 2: Enviando credenciales de login...")
    
    login_data = {
        'username': 'testuser',
        'password': 'Test123456'
    }
    
    # Headers que simula el navegador
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Referer': f'{base_url}/loginpage',
        'Origin': base_url,
        'X-Requested-With': 'XMLHttpRequest'  # Simular AJAX
    }
    
    try:
        # Probar con diferentes configuraciones
        configs = [
            {
                'name': 'Configuración básica',
                'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                'data': login_data
            },
            {
                'name': 'Configuración completa del navegador',
                'headers': headers,
                'data': login_data
            },
            {
                'name': 'Con URLSearchParams format',
                'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                'data': 'username=testuser&password=Test123456'
            }
        ]
        
        for i, config in enumerate(configs, 1):
            print(f"\n🧪 PRUEBA {i}: {config['name']}")
            print("-" * 30)
            
            try:
                response = session.post(
                    f"{base_url}/login",
                    headers=config['headers'],
                    data=config['data'],
                    allow_redirects=False,  # No seguir redirects automáticamente
                    timeout=10
                )
                
                print(f"Status: {response.status_code}")
                print(f"URL: {response.url}")
                print(f"Headers de respuesta:")
                for header, value in response.headers.items():
                    print(f"  {header}: {value}")
                
                if 'set-cookie' in response.headers:
                    print(f"Cookies establecidas: {response.headers['set-cookie']}")
                
                if response.status_code == 200:
                    try:
                        json_response = response.json()
                        print(f"✅ JSON válido recibido:")
                        print(json.dumps(json_response, indent=2, ensure_ascii=False))
                        
                        if 'access_token' in json_response:
                            print(f"🎫 Token de acceso: {json_response['access_token'][:50]}...")
                            
                    except json.JSONDecodeError:
                        print(f"❌ Respuesta no es JSON válido:")
                        print(f"  Contenido: {response.text[:200]}...")
                        
                elif response.status_code == 405:
                    print(f"❌ Error 405 - Método no permitido")
                    print(f"  Contenido: {response.text[:200]}...")
                    
                    # Verificar si es una página de error
                    if "405" in response.text and "html" in response.text.lower():
                        print(f"  ⚠️  Respuesta es página HTML de error, no JSON")
                        
                elif 300 <= response.status_code < 400:
                    print(f"🔄 Redirección {response.status_code}")
                    if 'location' in response.headers:
                        print(f"  Redirigiendo a: {response.headers['location']}")
                else:
                    print(f"❌ Error {response.status_code}")
                    print(f"  Contenido: {response.text[:200]}...")
                
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout en la petición")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de red: {e}")
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    print(f"\n" + "="*60)
    
    # Paso 3: Verificar el estado del servidor
    print("🔍 PASO 3: Verificando estado del servidor...")
    
    try:
        # Verificar endpoints disponibles
        endpoints_to_check = [
            '/login',
            '/loginpage', 
            '/admin',
            '/static/test_login_simple.html'
        ]
        
        for endpoint in endpoints_to_check:
            try:
                check_response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"  {endpoint}: {check_response.status_code}")
            except Exception as e:
                print(f"  {endpoint}: ERROR - {e}")
                
    except Exception as e:
        print(f"❌ Error verificando servidor: {e}")

if __name__ == "__main__":
    test_network_behavior()
