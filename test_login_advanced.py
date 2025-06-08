#!/usr/bin/env python3
"""
Script avanzado para diagnosticar el problema específico del endpoint POST /login
"""
import requests
import json

def detailed_login_test():
    """Diagnóstico detallado del endpoint POST /login"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 DIAGNÓSTICO AVANZADO DEL ENDPOINT POST /login")
    print("=" * 65)
    
    # 1. Verificar que el servidor responde
    try:
        health_response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Servidor responde: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Servidor no responde: {e}")
        return
    
    # 2. Verificar todas las variaciones del endpoint
    print(f"\n📋 VERIFICANDO TODAS LAS VARIACIONES DE LOGIN...")
    login_urls = [
        "/login",
        "/usuarios/login", 
        "/auth/login",
        "/api/login",
        "/user/login"
    ]
    
    for url in login_urls:
        try:
            # OPTIONS request
            options_resp = requests.options(f"{base_url}{url}", timeout=5)
            print(f"   OPTIONS {url}: {options_resp.status_code}")
            if "Allow" in options_resp.headers:
                print(f"      Allow: {options_resp.headers['Allow']}")
            
            # POST request con form data
            login_data = {"username": "juan", "password": "123456"}
            post_resp = requests.post(
                f"{base_url}{url}",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            print(f"   POST {url}: {post_resp.status_code}")
            if post_resp.status_code == 405 and "Allow" in post_resp.headers:
                print(f"      Allow: {post_resp.headers['Allow']}")
            elif post_resp.status_code == 200:
                print(f"      ✅ LOGIN EXITOSO!")
                try:
                    resp_json = post_resp.json()
                    if "access_token" in resp_json:
                        print(f"      ✅ Token recibido!")
                        return url  # Retornar la URL que funciona
                except:
                    pass
            elif post_resp.status_code == 422:
                print(f"      ⚠️ Error de validación")
            
        except Exception as e:
            print(f"   ❌ Error en {url}: {e}")
        print()
    
    # 3. Probar con diferentes headers y métodos
    print(f"📋 PROBANDO DIFERENTES CONFIGURACIONES EN /login...")
    
    configurations = [
        {
            "name": "Form Data estándar",
            "method": "POST",
            "data": {"username": "juan", "password": "123456"},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"}
        },
        {
            "name": "Form Data con User-Agent",
            "method": "POST", 
            "data": {"username": "juan", "password": "123456"},
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        },
        {
            "name": "Form Data con Accept",
            "method": "POST",
            "data": {"username": "juan", "password": "123456"},
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
        },
        {
            "name": "Multipart Form Data",
            "method": "POST",
            "files": {"username": ("", "juan"), "password": ("", "123456")},
            "headers": {}
        }
    ]
    
    for config in configurations:
        print(f"\n   🔹 {config['name']}:")
        try:
            kwargs = {
                "url": f"{base_url}/login",
                "timeout": 10,
                "headers": config["headers"]
            }
            
            if "data" in config:
                kwargs["data"] = config["data"]
            if "files" in config:
                kwargs["files"] = config["files"]
            
            response = requests.post(**kwargs)
            
            print(f"      Status: {response.status_code}")
            print(f"      Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"      ✅ ÉXITO!")
                try:
                    resp_json = response.json()
                    print(f"      Response: {json.dumps(resp_json, indent=2)[:200]}...")
                except:
                    print(f"      Response (text): {response.text[:200]}...")
            elif response.status_code == 405:
                print(f"      ❌ Método no permitido")
            elif response.status_code == 422:
                print(f"      ⚠️ Error de validación")
                print(f"      Response: {response.text[:300]}...")
            else:
                print(f"      Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 4. Inspeccionar la respuesta con curl equivalente
    print(f"\n🔧 COMANDOS CURL EQUIVALENTES:")
    print(f"   curl -X POST {base_url}/login \\")
    print(f"        -H 'Content-Type: application/x-www-form-urlencoded' \\")
    print(f"        -d 'username=juan&password=123456'")
    
    return None

if __name__ == "__main__":
    working_url = detailed_login_test()
