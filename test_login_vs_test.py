#!/usr/bin/env python3
"""
Script para probar el endpoint temporal /login-test vs /login
"""
import requests

def test_login_endpoints():
    """Comparar comportamiento de /login vs /login-test"""
    print("🧪 COMPARANDO /login vs /login-test")
    print("=" * 45)
    
    base_url = "http://localhost:8000"
    
    endpoints = ["/login", "/login-test"]
    
    for endpoint in endpoints:
        print(f"\n🔍 PROBANDO {endpoint}:")
        print("-" * 30)
        
        # Test OPTIONS
        try:
            options_resp = requests.options(f"{base_url}{endpoint}", timeout=5)
            print(f"   OPTIONS: Status {options_resp.status_code}")
            print(f"   Allow:   {options_resp.headers.get('Allow', 'No header')}")
        except Exception as e:
            print(f"   OPTIONS: Error - {e}")
        
        # Test POST
        try:
            post_resp = requests.post(
                f"{base_url}{endpoint}",
                data={"username": "admin", "password": "admin"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            print(f"   POST:    Status {post_resp.status_code}")
            print(f"   Allow:   {post_resp.headers.get('Allow', 'No header')}")
            
            if post_resp.status_code == 200:
                print(f"   ✅ ÉXITO: Endpoint funciona correctamente!")
                try:
                    data = post_resp.json()
                    if "access_token" in data:
                        print(f"   🎫 Token: {data['access_token'][:30]}...")
                except:
                    pass
            elif post_resp.status_code == 405:
                print(f"   ❌ Method Not Allowed - Problema confirmado")
            elif post_resp.status_code == 422:
                print(f"   ⚠️  Validation Error - Credenciales incorrectas")
            elif post_resp.status_code == 401:
                print(f"   🔐 Unauthorized - Credenciales incorrectas")
            else:
                print(f"   🤔 Status inesperado: {post_resp.text[:100]}")
                
        except Exception as e:
            print(f"   POST: Error - {e}")
        
        # Test GET (debería fallar)
        try:
            get_resp = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   GET:     Status {get_resp.status_code}")
            print(f"   Allow:   {get_resp.headers.get('Allow', 'No header')}")
        except Exception as e:
            print(f"   GET: Error - {e}")
    
    print("\n" + "=" * 45)
    print("🎯 ANÁLISIS:")
    print("   Si /login-test funciona pero /login no,")
    print("   entonces hay algo específico con la ruta /login")
    print("   Si ambos fallan igual, el problema es del sistema de routing")

if __name__ == "__main__":
    test_login_endpoints()
