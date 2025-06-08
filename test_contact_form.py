#!/usr/bin/env python3
"""
Test para verificar que el formulario de contacto envía correos correctamente
"""
import requests
import json
import sys
import os

# Configuración del servidor
BASE_URL = "http://localhost:8000"
ENDPOINT = "/envios/enviar_correo"

def test_contact_form_endpoint():
    """
    Prueba el endpoint de envío de correos del formulario de contacto
    """
    print("🧪 PROBANDO ENDPOINT DE FORMULARIO DE CONTACTO")
    print("=" * 60)
    
    # Datos de prueba simulando el formulario de contacto
    test_data = {
        "destinatario": "test@example.com",
        "asunto": "Nuevo contacto desde web - Juan Pérez",
        "mensaje": """Nuevo mensaje de contacto:

Nombre: Juan Pérez
Email: juan.perez@example.com
Empresa: Tech Solutions
Tipo de proyecto: Desarrollo de API

Mensaje:
Hola, estoy interesado en sus servicios de desarrollo de APIs. 
¿Podrían contactarme para discutir mi proyecto?"""
    }
    
    try:
        print(f"📡 Enviando POST a: {BASE_URL}{ENDPOINT}")
        print(f"📝 Datos enviados:")
        print(json.dumps(test_data, indent=2, ensure_ascii=False))
        print()
        
        # Realizar la petición
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Código de respuesta: {response.status_code}")
        print(f"📋 Headers de respuesta: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ÉXITO: {result}")
            print("\n🎉 El formulario de contacto funciona correctamente!")
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"💥 Detalle del error: {error_detail}")
            except:
                print(f"💥 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

def test_server_running():
    """
    Verifica que el servidor esté ejecutándose
    """
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor ejecutándose correctamente")
            return True
        else:
            print(f"⚠️ Servidor responde pero con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor no está ejecutándose")
        return False
    except Exception as e:
        print(f"❌ Error al verificar servidor: {e}")
        return False

def main():
    print("🚀 INICIANDO PRUEBAS DEL FORMULARIO DE CONTACTO")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    if not test_server_running():
        print("\n💡 Para ejecutar el servidor, usa:")
        print("   uvicorn sql_app.main:app --reload")
        return
    
    print()
    
    # Probar el endpoint
    success = test_contact_form_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 RESULTADO: ¡Todas las pruebas pasaron!")
        print("📧 El formulario de contacto está configurado correctamente")
    else:
        print("🔴 RESULTADO: Hay problemas con el formulario de contacto")
        print("🔧 Revisa la configuración del correo en el archivo .env")

if __name__ == "__main__":
    main()
