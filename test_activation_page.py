#!/usr/bin/env python3
"""Script para probar la nueva página de activación"""

import requests
import time

def test_activation_page():
    """Prueba la nueva página de activación"""
    base_url = "http://localhost:8000"
    
    print("🧪 PROBANDO NUEVA PÁGINA DE ACTIVACIÓN")
    print("=" * 50)
    
    try:
        # Probar la página HTML
        print("\n1. Probando endpoint de página de activación (/activar)...")
        response = requests.get(f"{base_url}/activar?token=test_token", timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Tamaño de respuesta: {len(response.content)} bytes")
        
        if response.status_code == 200:
            if "text/html" in response.headers.get('content-type', ''):
                print("✅ Página HTML servida correctamente")
                # Verificar que contiene elementos clave
                content = response.text
                if "Activando tu cuenta" in content:
                    print("✅ Contenido HTML correcto encontrado")
                else:
                    print("❌ Contenido HTML parece incorrecto")
            else:
                print("❌ No es una respuesta HTML")
        else:
            print(f"❌ Error en la página: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
        
        # Probar el endpoint API
        print("\n2. Probando endpoint API de activación (/api/activar)...")
        api_response = requests.post(
            f"{base_url}/api/activar",
            json={"token": "token_invalido_para_prueba"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {api_response.status_code}")
        print(f"Content-Type: {api_response.headers.get('content-type', 'Unknown')}")
        
        if api_response.status_code in [400, 422]:  # Se espera error por token inválido
            print("✅ API responde correctamente (error esperado por token inválido)")
            try:
                error_data = api_response.json()
                print(f"Error mensaje: {error_data.get('detail', 'No detail')}")
            except:
                print("Respuesta no es JSON válido")
        else:
            print(f"Status inesperado: {api_response.status_code}")
            print(f"Respuesta: {api_response.text[:200]}...")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está corriendo en http://localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("Esperando a que el servidor se inicie...")
    time.sleep(2)  # Dar tiempo para que el servidor se inicie
    
    success = test_activation_page()
    
    if success:
        print("\n🎉 Pruebas completadas. Revisa los resultados arriba.")
    else:
        print("\n💥 Algunas pruebas fallaron.")
