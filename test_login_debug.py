#!/usr/bin/env python3
"""
Script de prueba para debuggear el login
"""

import requests
import json

def test_login():
    """Probar el login y ver la respuesta"""
    
    # URL del endpoint de login
    url = "http://localhost:8000/login"
    
    # Datos de login (ajusta según tus credenciales de prueba)
    data = {
        'username': 'juan',  # Ajusta con tu usuario
        'password': '123456'  # Ajusta con tu contraseña
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print(f"🔍 Enviando petición POST a: {url}")
        print(f"📊 Datos enviados: {data}")
        print(f"📝 Headers: {headers}")
        
        # Hacer la petición
        response = requests.post(url, data=data, headers=headers)
        
        print(f"\n📊 RESPUESTA DEL SERVIDOR:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"✅ Respuesta JSON:")
                print(json.dumps(response_json, indent=2, ensure_ascii=False))
                
                # Verificar si tiene access_token
                if 'access_token' in response_json:
                    print(f"✅ Token de acceso encontrado: {response_json['access_token'][:50]}...")
                else:
                    print(f"❌ No se encontró 'access_token' en la respuesta")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al parsear JSON: {e}")
                print(f"Contenido crudo: {response.text}")
        else:
            print(f"❌ Error en la petición:")
            print(f"Código de estado: {response.status_code}")
            print(f"Mensaje: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_admin_endpoint():
    """Probar acceso al endpoint /admin"""
    
    url = "http://localhost:8000/admin"
    
    try:
        print(f"\n🔍 Probando acceso a: {url}")
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            print(f"✅ Endpoint /admin accesible")
            print(f"Contenido (primeros 200 chars): {response.text[:200]}...")
        else:
            print(f"❌ Error al acceder a /admin: {response.status_code}")
            print(f"Mensaje: {response.text}")
            
    except Exception as e:
        print(f"❌ Error al probar /admin: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBA DE DEBUG DE LOGIN")
    print("=" * 50)
    
    test_login()
    test_admin_endpoint()
    
    print("\n✅ Pruebas completadas")
