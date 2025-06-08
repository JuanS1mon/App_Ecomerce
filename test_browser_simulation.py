#!/usr/bin/env python3
"""
Script para simular exactamente el comportamiento del navegador
"""

import requests
import json
from urllib.parse import urlencode

def test_browser_simulation():
    """Simular exactamente lo que hace el navegador"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # 1. Primero obtener la página de login como haría el navegador
    print("📄 PASO 1: Obteniendo página de login...")
    login_page_response = session.get(f"{base_url}/loginpage")
    print(f"Status: {login_page_response.status_code}")
    
    # 2. Simular el envío del formulario exactamente como el JavaScript
    print("\n🔐 PASO 2: Simulando envío de formulario...")
    
    # Headers que envía el navegador
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': f'{base_url}/loginpage',
        'Origin': base_url,
    }
    
    # Datos del formulario
    form_data = {
        'username': 'juan',
        'password': 'Juan904068'
    }
    
    print(f"🎯 URL de destino: {base_url}/login")
    print(f"📊 Datos: {form_data}")
    print(f"📋 Headers: {headers}")
    
    # Hacer la petición
    try:
        response = session.post(
            f"{base_url}/login",
            data=urlencode(form_data),
            headers=headers,
            allow_redirects=False  # Para ver si hay redirects
        )
        
        print(f"\n📬 RESPUESTA:")
        print(f"✅ Status: {response.status_code}")
        print(f"🔗 URL: {response.url}")
        print(f"📋 Headers de respuesta:")
        for header, value in response.headers.items():
            print(f"    {header}: {value}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"\n✅ JSON de respuesta:")
                print(json.dumps(response_json, indent=2, ensure_ascii=False))
                
                if 'access_token' in response_json:
                    print(f"\n🎫 Token encontrado: {response_json['access_token'][:50]}...")
                    print("✅ LOGIN EXITOSO!")
                else:
                    print("❌ No se encontró token en la respuesta")
                    
            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido: {response.text[:200]}...")
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Probar también con fetch API simulation
    print(f"\n🌐 PASO 3: Probando diferentes configuraciones...")
    
    # Probar sin headers adicionales (más similar a fetch)
    simple_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        response2 = session.post(
            f"{base_url}/login",
            data=urlencode(form_data),
            headers=simple_headers,
            allow_redirects=False
        )
        
        print(f"Con headers simples - Status: {response2.status_code}")
        
    except Exception as e:
        print(f"Error con headers simples: {e}")

if __name__ == "__main__":
    print("🧪 SIMULACIÓN DE NAVEGADOR - LOGIN DEBUG")
    print("=" * 60)
    test_browser_simulation()
    print("\n✅ Prueba completada")
