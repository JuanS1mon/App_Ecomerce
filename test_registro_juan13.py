#!/usr/bin/env python3
"""
Test script para verificar el registro de usuario con nombre "juan13"
"""

import requests
import json

def test_registro_usuario():
    url = "http://127.0.0.1:8000/user/registro"
    
    # Datos de prueba que fallan actualmente
    datos_usuario = {
        "nombre": "juan13",  # Este es el que está causando el problema
        "usuario": "juan13_user",
        "clave": "123456",
        "mail": "juan13@example.com",
        "telefono": "+1234567890",
        "acepta_terminos": True
    }
    
    print("🧪 Probando registro de usuario...")
    print(f"📤 Enviando datos: {json.dumps(datos_usuario, indent=2)}")
    
    try:
        response = requests.post(url, json=datos_usuario)
        
        print(f"\n📨 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 422:
            print("❌ Error 422 - Datos de validación:")
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
            
            # Mostrar detalles específicos del error
            if "detail" in error_data and isinstance(error_data["detail"], list):
                for error in error_data["detail"]:
                    print(f"\n🔍 Campo: {error.get('loc', [])}")
                    print(f"💬 Mensaje: {error.get('msg', 'Sin mensaje')}")
                    print(f"📝 Valor enviado: {error.get('input', 'Sin valor')}")
                    
        elif response.status_code == 201:
            print("✅ Registro exitoso!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. ¿Está ejecutándose en http://127.0.0.1:8000?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_registro_usuario_nombre_valido():
    """Prueba con un nombre más tradicional para comparar"""
    url = "http://127.0.0.1:8000/user/registro"
    
    datos_usuario = {
        "nombre": "Juan Carlos",  # Nombre más tradicional
        "usuario": "juan_carlos_user",
        "clave": "123456",
        "mail": "juan.carlos@example.com",
        "telefono": "+1234567890",
        "acepta_terminos": True
    }
    
    print("\n🧪 Probando registro con nombre tradicional...")
    print(f"📤 Enviando datos: {json.dumps(datos_usuario, indent=2)}")
    
    try:
        response = requests.post(url, json=datos_usuario)
        print(f"\n📨 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Registro exitoso con nombre tradicional!")
        elif response.status_code == 422:
            print("❌ Falló incluso con nombre tradicional:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"⚠️  Respuesta: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registro_usuario()
    test_registro_usuario_nombre_valido()
