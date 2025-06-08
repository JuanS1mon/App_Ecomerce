# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de correo con caracteres especiales
"""

import requests
import json

def test_endpoint_correo():
    """
    Prueba el endpoint de envío de correo con caracteres especiales
    """
    url = "http://localhost:8000/envios/enviar_correo"
    
    # Datos con caracteres especiales
    data = {
        "destinatario": "test@ejemplo.com",  # Cambia por un email real para probar
        "asunto": "Prueba de contraseña y configuración",
        "mensaje": "Este mensaje contiene caracteres especiales: año, niño, configuración, información. ¿Funciona correctamente? ¡Esperamos que sí!"
    }
    
    try:
        print("🧪 Enviando solicitud al endpoint...")
        print(f"URL: {url}")
        print(f"Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=data)
        
        print(f"\n📊 Respuesta:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint funcionando correctamente con caracteres especiales")
        else:
            print(f"❌ Error en el endpoint: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose?")
        print("   Ejecuta: uvicorn sql_app.main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Probando endpoint de correo con caracteres especiales...")
    test_endpoint_correo()
