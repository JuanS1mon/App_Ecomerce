# -*- coding: utf-8 -*-
"""
Script de prueba completa para el flujo de reset de contraseña corregido
"""

import requests
import json
import time
import re
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_complete_password_reset_flow():
    """
    Prueba el flujo completo de reset de contraseña
    """
    print("🔄 Probando flujo completo de reset de contraseña...")
    
    # Datos de prueba
    test_email = "fjuansimon@gmail.com"  # Usa tu email real para recibir el correo
    
    # Paso 1: Solicitar reset de contraseña
    print("\n📧 Paso 1: Solicitando reset de contraseña...")
    reset_request_url = f"{BASE_URL}/password-reset-request"
    
    reset_data = {
        "email": test_email
    }
    
    try:
        response = requests.post(reset_request_url, json=reset_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Solicitud de reset enviada correctamente")
            print("📬 Revisa tu correo electrónico para obtener el enlace de reset")
            
            # Instrucciones para el usuario
            print("\n" + "="*60)
            print("INSTRUCCIONES PARA COMPLETAR LA PRUEBA:")
            print("="*60)
            print("1. Revisa tu correo electrónico")
            print("2. Busca el correo con asunto 'Restablecimiento de contraseña'")
            print("3. Haz clic en el enlace del correo")
            print("4. Deberías ver la página para ingresar nueva contraseña")
            print("5. El enlace debería ser algo como:")
            print("   http://localhost:8000/confirm-password-reset?token=...")
            print("6. Ingresa una nueva contraseña y confirma")
            print("="*60)
            
            return True
        else:
            print(f"❌ Error al solicitar reset: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reset_page_access():
    """
    Prueba que las páginas de reset sean accesibles
    """
    print("\n🌐 Probando acceso a las páginas de reset...")
    
    # Página de solicitud de reset
    try:
        response = requests.get(f"{BASE_URL}/reset-password", timeout=5)
        if response.status_code == 200:
            print("✅ Página de solicitud de reset accesible")
        else:
            print(f"❌ Error en página de solicitud: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo a solicitud de reset: {e}")
    
    # Página de confirmación de reset (sin token)
    try:
        response = requests.get(f"{BASE_URL}/confirm-password-reset", timeout=5)
        if response.status_code == 200:
            print("✅ Página de confirmación de reset accesible")
        else:
            print(f"❌ Error en página de confirmación: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo a confirmación de reset: {e}")

def test_with_dummy_token():
    """
    Prueba el endpoint de confirmación con un token dummy para verificar validación
    """
    print("\n🧪 Probando validación de token...")
    
    dummy_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.dummy.token"
    
    confirm_data = {
        "token": dummy_token,
        "new_password": "nueva123",
        "confirm_password": "nueva123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/confirm-password-reset", 
                               json=confirm_data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Validación de token funcionando (token inválido rechazado)")
        else:
            print(f"⚠️ Respuesta inesperada: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_password_validation():
    """
    Prueba la validación de contraseñas
    """
    print("\n🔒 Probando validación de contraseñas...")
    
    dummy_token = "valid.token.dummy"
    
    # Contraseñas que no coinciden
    test_cases = [
        {
            "name": "Contraseñas no coinciden",
            "data": {
                "token": dummy_token,
                "new_password": "nueva123",
                "confirm_password": "otra456"
            },
            "expected_error": "Las contraseñas no coinciden"
        },
        {
            "name": "Contraseña muy corta",
            "data": {
                "token": dummy_token,
                "new_password": "12",
                "confirm_password": "12"
            },
            "expected_error": "La contraseña debe tener al menos 3 caracteres"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nProbando: {test_case['name']}")
        try:
            response = requests.post(f"{BASE_URL}/confirm-password-reset", 
                                   json=test_case['data'], timeout=10)
            
            if response.status_code == 422:
                print(f"✅ Validación funcionando: {test_case['name']}")
            else:
                print(f"⚠️ Validación inesperada: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del flujo de reset de contraseña corregido...")
    
    # Verificar que el servidor esté funcionando
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Servidor accesible")
    except Exception:
        print("❌ Servidor no accesible. Asegúrate de que esté corriendo:")
        print("   uvicorn sql_app.main:app --reload")
        exit(1)
    
    # Ejecutar pruebas
    test_reset_page_access()
    test_password_validation()
    test_with_dummy_token()
    test_complete_password_reset_flow()
    
    print("\n✅ Pruebas completadas.")
    print("\n💡 Puntos clave del flujo corregido:")
    print("   1. /reset-password - Página para solicitar reset")
    print("   2. /password-reset-request - Endpoint para enviar email")
    print("   3. /confirm-password-reset - Página para cambiar contraseña con token")
    print("   4. /confirm-password-reset - Endpoint para confirmar nueva contraseña")
    print("\n🔗 El enlace del correo ahora apunta a /confirm-password-reset?token=...")
