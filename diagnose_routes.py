#!/usr/bin/env python3
"""
Script para diagnosticar rutas disponibles en el servidor FastAPI
"""
import requests
import sys

def diagnose_routes():
    """Diagnostica qué rutas están disponibles y funcionando"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 DIAGNÓSTICO DE RUTAS DEL SERVIDOR")
    print("=" * 50)
    
    # Lista de rutas que debería tener la aplicación
    routes_to_test = [
        # Rutas principales
        ("/", "GET"),
        ("/docs", "GET"),
        ("/openapi.json", "GET"),
        
        # Rutas de usuarios (sin prefijo según usuarios.py)
        ("/login", "GET"),
        ("/login", "POST"),
        ("/loginpage", "GET"),
        ("/logout", "POST"),
        ("/reset-password", "GET"),
        ("/reset-password", "POST"),
        ("/confirm-password-reset", "POST"),
        
        # Rutas de admin
        ("/admin", "GET"),
        
        # Rutas con posibles prefijos
        ("/usuarios/login", "POST"),
        ("/auth/login", "POST"),
        ("/api/login", "POST"),
    ]
    
    print(f"\n📊 PROBANDO {len(routes_to_test)} RUTAS...")
    working_routes = []
    
    for route, method in routes_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{route}", timeout=5)
            elif method == "POST":
                # Para POST, usar datos mínimos
                response = requests.post(
                    f"{base_url}{route}", 
                    data={"username": "test", "password": "test"},
                    timeout=5
                )
            
            status = response.status_code
            if status < 500:  # No es error del servidor
                working_routes.append((route, method, status))
                status_icon = "✅" if status < 400 else "⚠️" if status < 500 else "❌"
                print(f"   {status_icon} {method} {route}: {status}")
            else:
                print(f"   ❌ {method} {route}: {status} (Error del servidor)")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 {method} {route}: Error de conexión")
    
    print(f"\n📋 RESUMEN:")
    print(f"   🟢 Rutas que responden: {len(working_routes)}")
    
    # Analizar rutas de login específicamente
    login_routes = [wr for wr in working_routes if "login" in wr[0].lower()]
    print(f"   🔐 Rutas de login encontradas: {len(login_routes)}")
    
    for route, method, status in login_routes:
        print(f"      • {method} {route}: {status}")
    
    # Verificar admin
    admin_routes = [wr for wr in working_routes if "admin" in wr[0].lower()]
    print(f"   🏛️ Rutas de admin encontradas: {len(admin_routes)}")
    
    for route, method, status in admin_routes:
        print(f"      • {method} {route}: {status}")
    
    return working_routes

def test_specific_login_methods():
    """Prueba métodos específicos de login que podrían estar funcionando"""
    base_url = "http://127.0.0.1:8000"
    
    print(f"\n🔐 PROBANDO MÉTODOS DE LOGIN ESPECÍFICOS...")
    print("-" * 40)
    
    # Diferentes formas de hacer login
    login_attempts = [
        {
            "name": "Form Data estándar",
            "url": f"{base_url}/login",
            "method": "POST",
            "data": {"username": "juan", "password": "123456"},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"}
        },
        {
            "name": "JSON Data",
            "url": f"{base_url}/login", 
            "method": "POST",
            "json": {"username": "juan", "password": "123456"},
            "headers": {"Content-Type": "application/json"}
        },
        {
            "name": "GET a loginpage",
            "url": f"{base_url}/loginpage",
            "method": "GET",
            "data": None,
            "headers": {}
        }
    ]
    
    for attempt in login_attempts:
        try:
            print(f"\n   Probando: {attempt['name']}")
            
            if attempt["method"] == "GET":
                response = requests.get(attempt["url"], headers=attempt.get("headers", {}))
            else:
                if "json" in attempt:
                    response = requests.post(
                        attempt["url"], 
                        json=attempt["json"],
                        headers=attempt.get("headers", {})
                    )
                else:
                    response = requests.post(
                        attempt["url"], 
                        data=attempt.get("data", {}),
                        headers=attempt.get("headers", {})
                    )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ ÉXITO con {attempt['name']}")
                try:
                    json_response = response.json()
                    if "access_token" in json_response:
                        print(f"   🎉 Token obtenido exitosamente")
                        return True
                except:
                    pass
            elif response.status_code == 422:
                print(f"   ⚠️  Error de validación: {response.text[:100]}...")
            elif response.status_code == 405:
                print(f"   ❌ Método no permitido")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    return False

def main():
    print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DEL SERVIDOR")
    
    # 1. Verificar que el servidor responde
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Servidor responde: {response.status_code}")
    except:
        print("❌ Servidor no responde")
        return False
    
    # 2. Diagnosticar rutas
    working_routes = diagnose_routes()
    
    # 3. Probar métodos de login específicos
    login_success = test_specific_login_methods()
    
    print(f"\n" + "=" * 50)
    print(f"🏁 DIAGNÓSTICO COMPLETADO")
    print(f"   Total rutas encontradas: {len(working_routes)}")
    print(f"   Login funcional: {'✅' if login_success else '❌'}")
    
    if not login_success:
        print(f"\n💡 SUGERENCIAS:")
        print(f"   1. Verificar configuración de rutas en main.py")
        print(f"   2. Revisar errores en usuarios.py")
        print(f"   3. Verificar importaciones de security_improved.py")
    
    return login_success

if __name__ == "__main__":
    main()
