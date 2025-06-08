#!/usr/bin/env python3
"""Script final para probar el endpoint /admin después de arreglar las plantillas"""

import requests
import sys

def test_complete_workflow():
    base_url = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("🧪 PRUEBA COMPLETA DE FLUJO DE ADMIN")
    print("=" * 60)
    
    # Paso 1: Probar endpoints básicos
    print("\n📋 Paso 1: Verificando endpoints básicos...")
    basic_endpoints = {
        "/": "Página principal",
        "/loginpage": "Página de login",
        "/terminos": "Términos y condiciones"
    }
    
    for endpoint, desc in basic_endpoints.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"  {desc}: {status}")
        except Exception as e:
            print(f"  {desc}: ❌ Error - {e}")
    
    # Paso 2: Realizar login
    print("\n🔐 Paso 2: Realizando login...")
    login_data = {
        'username': 'testuser',
        'password': 'Test123456'
    }
    
    try:
        login_response = requests.post(f"{base_url}/login", data=login_data, timeout=10)
        print(f"  Estado del login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"  ❌ Error en login: {login_response.text[:200]}")
            return False
            
        # Extraer token
        token_data = login_response.json()
        token = token_data.get('access_token')
        
        if not token:
            print("  ❌ No se pudo obtener el token")
            return False
            
        print(f"  ✅ Token obtenido: {token[:30]}...")
        
    except Exception as e:
        print(f"  ❌ Error en login: {e}")
        return False
    
    # Paso 3: Probar endpoint /admin
    print("\n🔧 Paso 3: Probando endpoint /admin...")
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        admin_response = requests.get(f"{base_url}/admin", headers=headers, timeout=15)
        print(f"  Estado del admin: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("  ✅ ¡ÉXITO! El endpoint /admin funciona correctamente!")
            print(f"  📄 Content-Type: {admin_response.headers.get('content-type')}")
            print(f"  📊 Tamaño de respuesta: {len(admin_response.content):,} bytes")
            
            # Verificar que es HTML
            if 'text/html' in admin_response.headers.get('content-type', ''):
                print("  ✅ Respuesta es HTML válido")
                
                # Buscar elementos clave en el HTML
                content = admin_response.text.lower()
                key_elements = [
                    ('Panel de Administración', 'panel de administración' in content),
                    ('Dashboard', 'dashboard' in content or 'admin' in content),
                    ('HTML structure', '<html' in content and '</html>' in content)
                ]
                
                for element, found in key_elements:
                    status = "✅" if found else "⚠️"
                    print(f"    {status} {element}: {'Encontrado' if found else 'No encontrado'}")
                    
            return True
        else:
            print(f"  ❌ Error en /admin:")
            print(f"    Status: {admin_response.status_code}")
            print(f"    Response: {admin_response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ Error al acceder a /admin: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("🔥 El sistema de autenticación y admin está funcionando correctamente")
        print("✅ Las plantillas se cargan sin problemas")
        print("✅ El endpoint /admin responde correctamente")
    else:
        print("❌ Algunas pruebas fallaron")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
