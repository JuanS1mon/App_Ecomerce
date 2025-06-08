#!/usr/bin/env python3
"""
Script para diagnosticar específicamente el endpoint POST /login
"""
import requests
import json

def test_login_endpoint():
    """Diagnóstico completo del endpoint POST /login"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 DIAGNÓSTICO ESPECÍFICO DEL ENDPOINT POST /login")
    print("=" * 60)
    
    # 1. Verificar que el servidor responde
    try:
        health_response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Servidor responde: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Servidor no responde: {e}")
        return
    
    # 2. Probar OPTIONS en /login para ver métodos permitidos
    print(f"\n📋 VERIFICANDO MÉTODOS PERMITIDOS EN /login...")
    try:
        options_response = requests.options(f"{base_url}/login")
        print(f"   OPTIONS /login: {options_response.status_code}")
        if "Allow" in options_response.headers:
            print(f"   ✅ Métodos permitidos: {options_response.headers['Allow']}")
        else:
            print(f"   ❌ No hay header 'Allow' en la respuesta")
            print(f"   Headers: {dict(options_response.headers)}")
    except Exception as e:
        print(f"   ❌ Error en OPTIONS: {e}")
    
    # 3. Probar GET en /login 
    print(f"\n📋 VERIFICANDO GET /login...")
    try:
        get_response = requests.get(f"{base_url}/login")
        print(f"   GET /login: {get_response.status_code}")
        if get_response.status_code == 405:
            print(f"   ⚠️ Método no permitido - confirma que POST debería funcionar")
            if "Allow" in get_response.headers:
                print(f"   Métodos permitidos según GET: {get_response.headers['Allow']}")
    except Exception as e:
        print(f"   ❌ Error en GET: {e}")
    
    # 4. Probar POST en /login con diferentes formatos
    print(f"\n🔐 PROBANDO POST /login CON DIFERENTES FORMATOS...")
    
    login_attempts = [
        {
            "name": "OAuth2 Form Data (estándar)",
            "data": {"username": "juan", "password": "123456"},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "method": "data"
        },
        {
            "name": "OAuth2 Form Data con grant_type",
            "data": {"username": "juan", "password": "123456", "grant_type": "password"},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "method": "data"
        },
        {
            "name": "JSON Data",
            "data": {"username": "juan", "password": "123456"},
            "headers": {"Content-Type": "application/json"},
            "method": "json"
        }
    ]
    
    for attempt in login_attempts:
        print(f"\n   🔹 {attempt['name']}:")
        try:
            if attempt["method"] == "data":
                response = requests.post(
                    f"{base_url}/login",
                    data=attempt["data"],
                    headers=attempt["headers"],
                    timeout=10
                )
            else:
                response = requests.post(
                    f"{base_url}/login",
                    json=attempt["data"],
                    headers=attempt["headers"],
                    timeout=10
                )
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 405:
                print(f"      ❌ Método no permitido")
                if "Allow" in response.headers:
                    print(f"      Métodos permitidos: {response.headers['Allow']}")
            elif response.status_code == 200:
                print(f"      ✅ Login exitoso!")
                try:
                    json_resp = response.json()
                    if "access_token" in json_resp:
                        print(f"      ✅ Token recibido (longitud: {len(json_resp['access_token'])})")
                except:
                    pass
            elif response.status_code == 422:
                print(f"      ⚠️ Error de validación - formato incorrecto")
                print(f"      Response: {response.text[:200]}...")
            else:
                print(f"      ⚠️ Respuesta inesperada")
                print(f"      Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 5. Verificar otros endpoints relacionados
    print(f"\n📍 VERIFICANDO ENDPOINTS RELACIONADOS...")
    related_endpoints = ["/loginpage", "/users/me", "/check-auth", "/logout"]
    
    for endpoint in related_endpoints:
        try:
            resp = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   GET {endpoint}: {resp.status_code}")
        except Exception as e:
            print(f"   GET {endpoint}: ERROR - {e}")

if __name__ == "__main__":
    test_login_endpoint()
