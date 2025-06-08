#!/usr/bin/env python3
"""
Prueba para verificar que el endpoint /usuarios_admin/ funciona correctamente
después de las correcciones aplicadas.
"""

import requests
import json
from datetime import datetime

def test_usuarios_admin_endpoint():
    """Prueba el endpoint de usuarios admin para verificar las correcciones"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Probando endpoint /usuarios_admin/ después de las correcciones...")
    print("=" * 60)
    
    try:
        # Probar acceso al endpoint principal
        print("1. Probando acceso a /usuarios_admin/")
        response = requests.get(f"{base_url}/usuarios_admin/", timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            print("   ✅ Endpoint responde correctamente")
            print(f"   📄 Tamaño de respuesta: {len(response.content)} bytes")
            
            # Verificar que es HTML
            if 'text/html' in response.headers.get('content-type', ''):
                print("   ✅ Respuesta es HTML válido")
                
                # Verificar que contiene elementos esperados
                content = response.text
                if 'Gestión de Usuarios' in content:
                    print("   ✅ Template cargado correctamente - título encontrado")
                else:
                    print("   ⚠️  Template cargado pero puede no ser el correcto")
                    
            else:
                print("   ⚠️  Respuesta no es HTML")
                
        elif response.status_code == 401:
            print("   ⚠️  Requiere autenticación (esperado)")
        elif response.status_code == 403:
            print("   ⚠️  Acceso denegado - requiere rol admin (esperado)")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📝 Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: No se puede conectar al servidor")
        print("   💡 Asegúrate de que uvicorn esté corriendo en http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        print("   ❌ Error: Timeout al conectar")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
    
    print("\n" + "=" * 60)
    
    # Probar endpoints de API
    print("2. Probando endpoints de API...")
    api_endpoints = [
        "/usuarios_admin/usuarios/",
        "/usuarios_admin/roles/",
    ]
    
    for endpoint in api_endpoints:
        try:
            print(f"   Probando {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print("   ✅ Requiere autenticación (correcto)")
            elif response.status_code == 200:
                print("   ✅ Respuesta exitosa")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_usuarios_admin_endpoint()
