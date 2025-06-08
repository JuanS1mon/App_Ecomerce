# -*- coding: utf-8 -*-
"""
Test específico para probar el reset de contraseña con caracteres especiales
"""

import requests
import json

def test_password_reset_request():
    """
    Prueba la solicitud de reset de contraseña con caracteres especiales
    """
    url = "http://localhost:8000/password-reset-request"
    
    # Datos con caracteres especiales en español
    data = {
        "email": "test@ejemplo.com"  # Usa un email real para probar
    }
    
    try:
        print("🧪 Enviando solicitud de reset de contraseña...")
        print(f"URL: {url}")
        print(f"Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=data)
        
        print(f"\n📊 Respuesta:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Reset de contraseña funcionando correctamente con caracteres especiales")
        elif response.status_code == 422:
            print("⚠️ Error de validación - verifica el formato del email")
        else:
            print(f"❌ Error en el endpoint: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose?")
        print("   Ejecuta: uvicorn sql_app.main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_form_based_reset():
    """
    Prueba el reset usando form data (como desde un formulario HTML)
    """
    url = "http://localhost:8000/reset-password"
    
    # Datos como formulario
    data = {
        "username": "test@ejemplo.com",  # En este caso username es el email
        "password": ""  # No usado para request
    }
    
    try:
        print("\n🧪 Enviando solicitud de reset (form-based)...")
        print(f"URL: {url}")
        
        response = requests.post(url, data=data)
        
        print(f"\n📊 Respuesta:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Form-based reset funcionando correctamente")
        else:
            print(f"❌ Error en el endpoint: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Probando reset de contraseña con caracteres especiales...")
    
    # Probar ambos métodos
    test_password_reset_request()
    test_form_based_reset()
    
    print("\n✅ Pruebas de reset de contraseña completadas.")
    print("\n💡 Si ves errores de conexión, asegúrate de que el servidor esté ejecutándose:")
    print("   uvicorn sql_app.main:app --reload")
