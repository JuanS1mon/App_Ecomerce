#!/usr/bin/env python3
"""
Script para detectar interceptación de métodos HTTP en el endpoint /login
"""
import requests
import json

def test_method_interception():
    """Detecta si algún middleware está interceptando/reescribiendo métodos HTTP"""
    print("🕵️ DETECTANDO INTERCEPTACIÓN DE MÉTODOS HTTP")
    print("=" * 55)
    
    base_url = "http://localhost:8000"
    
    # Headers estándar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    
    print("\n🔍 ANALIZANDO RESPUESTAS DE MÉTODOS HTTP EN /login:")
    print("-" * 55)
    
    methods_to_test = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    
    for method in methods_to_test:
        try:
            if method == "POST":
                # POST con form data (OAuth2 estándar)
                response = requests.request(
                    method, 
                    f"{base_url}/login",
                    data={"username": "admin", "password": "admin"},
                    headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )
            else:
                # Otros métodos sin body
                response = requests.request(
                    method, 
                    f"{base_url}/login",
                    headers=headers,
                    timeout=10
                )
            
            print(f"📋 {method:7} /login:")
            print(f"   Status: {response.status_code}")
            print(f"   Allow:  {response.headers.get('Allow', 'No header')}")
            print(f"   Type:   {response.headers.get('Content-Type', 'No header')[:40]}")
            
            # Detectar patrones anómalos
            if method == "POST" and response.status_code == 405:
                allow_header = response.headers.get('Allow', '')
                if 'GET' in allow_header and 'POST' not in allow_header:
                    print(f"   🚨 ANOMALÍA: POST devuelve Allow: {allow_header}")
                    print(f"   🧐 Esto sugiere interceptación de método HTTP")
            
            if method == "OPTIONS" and response.status_code == 405:
                allow_header = response.headers.get('Allow', '')
                if 'POST' in allow_header:
                    print(f"   ✅ NORMAL: OPTIONS reporta POST como permitido")
                else:
                    print(f"   ⚠️  RARO: OPTIONS no reporta POST como permitido")
            
            # Revisar si hay headers de redirección o proxy
            location = response.headers.get('Location')
            if location:
                print(f"   🔄 Location: {location}")
            
            server = response.headers.get('Server')
            if server:
                print(f"   🖥️  Server: {server}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error en {method}: {e}")
    
    print("\n🔍 VERIFICACIONES ADICIONALES:")
    print("-" * 40)
    
    # Test: Verificar si el problema es específico de /login
    test_endpoints = ["/docs", "/", "/admin", "/loginpage"]
    
    for endpoint in test_endpoints:
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                data={"test": "data"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            print(f"POST {endpoint:12}: Status {response.status_code}, Allow: {response.headers.get('Allow', 'N/A')}")
        except Exception as e:
            print(f"POST {endpoint:12}: Error - {e}")
    
    print("\n🔍 VERIFICANDO POTENCIALES INTERCEPTORES:")
    print("-" * 45)
    
    # Test: Verificar headers que podrían indicar proxies/middleware
    try:
        response = requests.post(
            f"{base_url}/login",
            data={"username": "test", "password": "test"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-HTTP-Method-Override": "POST",  # Header común en algunos proxies
            },
            timeout=10
        )
        
        suspicious_headers = [
            "X-Forwarded-For",
            "X-Real-IP", 
            "X-Forwarded-Proto",
            "X-Forwarded-Host",
            "Via",
            "X-Cache",
            "X-Proxy-Cache",
            "CF-Ray",  # Cloudflare
            "X-Served-By",
            "X-Cache-Status"
        ]
        
        found_proxy_headers = []
        for header in suspicious_headers:
            if header in response.headers:
                found_proxy_headers.append(f"{header}: {response.headers[header]}")
        
        if found_proxy_headers:
            print("⚠️  HEADERS DE PROXY/CACHE DETECTADOS:")
            for header in found_proxy_headers:
                print(f"   {header}")
        else:
            print("✅ No se detectaron headers de proxy/cache")
        
        # Verificar headers de CORS
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers",
            "Access-Control-Max-Age"
        ]
        
        found_cors_headers = []
        for header in cors_headers:
            if header in response.headers:
                found_cors_headers.append(f"{header}: {response.headers[header]}")
        
        if found_cors_headers:
            print("\n🌐 HEADERS DE CORS DETECTADOS:")
            for header in found_cors_headers:
                print(f"   {header}")
                
            # Verificar si CORS permite POST
            allow_methods = response.headers.get("Access-Control-Allow-Methods", "")
            if "POST" not in allow_methods and "*" not in allow_methods:
                print("   🚨 POSIBLE PROBLEMA: CORS no permite explícitamente POST")
        else:
            print("✅ No se detectaron headers CORS problemáticos")
            
    except Exception as e:
        print(f"❌ Error en verificación de interceptores: {e}")
    
    print("\n" + "=" * 55)
    print("🎯 CONCLUSIONES:")
    print("   Si POST /login devuelve 'Allow: GET', pero OPTIONS /login")
    print("   devuelve 'Allow: POST', entonces hay un interceptor que:")
    print("   1. Está reescribiendo las respuestas POST")
    print("   2. O está redirigiendo POST a GET internamente")
    print("   3. O hay un bug en FastAPI/Starlette routing")

if __name__ == "__main__":
    test_method_interception()
