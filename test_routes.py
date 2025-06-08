#!/usr/bin/env python3
"""
Script para probar las rutas HTML del servidor
"""

import requests
import time

def test_routes():
    """Prueba las rutas principales de HTML"""
    base_url = "http://localhost:8001"
    
    routes_to_test = [
        "/loginpage",
        "/registerpage", 
        "/",
        "/index",
        "/terminos",
        "/privacidad"
    ]
    
    print("🌐 Probando rutas del servidor...")
    print(f"🎯 Servidor base: {base_url}")
    
    # Esperar un poco para que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(3)
    
    for route in routes_to_test:
        try:
            url = f"{base_url}{route}"
            print(f"\n🔍 Probando: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_length = len(response.content)
                content_type = response.headers.get('content-type', 'Unknown')
                print(f"✅ {route} - OK (Código: {response.status_code}, Tamaño: {content_length} bytes, Tipo: {content_type})")
                
                # Verificar que sea HTML
                if 'html' in content_type.lower():
                    if '<html' in response.text.lower():
                        print(f"   📄 Contenido HTML válido detectado")
                    else:
                        print(f"   ⚠️  Respuesta no parece ser HTML válido")
                else:
                    print(f"   ⚠️  Tipo de contenido inesperado: {content_type}")
                    
            else:
                print(f"❌ {route} - Error {response.status_code}")
                print(f"   📝 Respuesta: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {route} - Error de conexión (¿servidor no iniciado?)")
        except requests.exceptions.Timeout:
            print(f"❌ {route} - Timeout")
        except Exception as e:
            print(f"❌ {route} - Error: {e}")

def test_static_files():
    """Prueba el acceso directo a archivos estáticos"""
    base_url = "http://localhost:8001"
    
    static_files = [
        "/static/login.html",
        "/static/register.html",
        "/static/index.html"
    ]
    
    print(f"\n📁 Probando archivos estáticos directamente...")
    
    for static_file in static_files:
        try:
            url = f"{base_url}{static_file}"
            print(f"\n🔍 Probando: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_length = len(response.content)
                print(f"✅ {static_file} - OK (Tamaño: {content_length} bytes)")
            else:
                print(f"❌ {static_file} - Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {static_file} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de rutas...")
    test_routes()
    test_static_files()
    print("\n✅ Pruebas completadas!")
