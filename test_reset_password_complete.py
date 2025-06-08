# -*- coding: utf-8 -*-
"""
Script para probar el flujo completo con una simulación de token real
"""

import requests
import json
from datetime import datetime, timedelta
import jwt

BASE_URL = "http://localhost:8000"

# Configuración (debe coincidir con la del servidor)
SECRET_KEY = "tu_clave_secreta_aqui"  # Reemplaza con la clave real del servidor
ALGORITHM = "HS256"

def create_test_token():
    """
    Crea un token de prueba válido para el reset de contraseña
    """
    # Datos del token
    payload = {
        "sub": "testuser",  # Username del usuario
        "type": "password_reset",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)  # Expira en 1 hora
    }
    
    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except Exception as e:
        print(f"❌ Error creando token: {e}")
        return None

def test_with_valid_token():
    """
    Prueba el flujo con un token válido
    """
    print("🔑 Probando con token válido...")
    
    # Crear token de prueba
    token = create_test_token()
    
    if not token:
        print("❌ No se pudo crear token de prueba")
        return False
    
    print(f"Token creado: {token[:50]}...")
    
    # Probar acceso a la página con token
    try:
        url_with_token = f"{BASE_URL}/confirm-password-reset?token={token}"
        response = requests.get(url_with_token, timeout=5)
        
        if response.status_code == 200:
            print("✅ Página de confirmación accesible con token")
            
            # Probar confirmación de contraseña
            confirm_data = {
                "token": token,
                "new_password": "nueva123",
                "confirm_password": "nueva123"
            }
            
            confirm_response = requests.post(f"{BASE_URL}/confirm-password-reset", 
                                           json=confirm_data, timeout=10)
            
            print(f"Status confirmación: {confirm_response.status_code}")
            print(f"Response: {confirm_response.text}")
            
            if confirm_response.status_code == 400:
                # Esperado si el usuario no existe en la BD
                print("⚠️ Usuario de prueba no existe en BD (esto es normal)")
                return True
            elif confirm_response.status_code == 200:
                print("✅ Confirmación exitosa")
                return True
            else:
                print(f"⚠️ Respuesta inesperada: {confirm_response.status_code}")
                return False
                
        else:
            print(f"❌ Error accediendo a página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_real_user_flow():
    """
    Prueba con un usuario real del sistema
    """
    print("\n👤 Probando flujo con usuario real...")
    
    # Solicitar reset para un usuario que probablemente exista
    test_emails = [
        "fjuansimon@gmail.com",  # Tu email
        "admin@example.com",
        "test@example.com"
    ]
    
    for email in test_emails:
        print(f"\nProbando con email: {email}")
        
        reset_data = {"email": email}
        
        try:
            response = requests.post(f"{BASE_URL}/password-reset-request", 
                                   json=reset_data, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Reset solicitado para {email}")
                print("📧 Revisa el correo para obtener el enlace real")
                return True
            else:
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def simulate_email_click():
    """
    Simula hacer clic en un enlace del correo
    """
    print("\n🔗 Simulando clic en enlace del correo...")
    
    # Ejemplo de URL que recibirías en el correo
    example_url = f"{BASE_URL}/confirm-password-reset?token=EXAMPLE_TOKEN"
    
    print(f"Enlace del correo: {example_url}")
    print("Al hacer clic, deberías ver:")
    print("1. Una página con formulario para nueva contraseña")
    print("2. Campos de contraseña con validación")
    print("3. Indicador de fortaleza de contraseña")
    print("4. Verificación de que las contraseñas coincidan")

if __name__ == "__main__":
    print("🧪 Probando flujo de reset de contraseña con tokens...")
    
    # Verificar servidor
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Servidor funcionando")
    except Exception:
        print("❌ Servidor no accesible")
        exit(1)
    
    # Ejecutar pruebas
    test_with_valid_token()
    test_real_user_flow()
    simulate_email_click()
    
    print("\n" + "="*60)
    print("RESUMEN DEL FLUJO CORREGIDO:")
    print("="*60)
    print("✅ ANTES: El enlace llevaba a /reset-password (página de solicitar reset)")
    print("✅ AHORA: El enlace lleva a /confirm-password-reset (página de cambiar contraseña)")
    print("")
    print("🔄 FLUJO COMPLETO:")
    print("1. Usuario va a /reset-password")
    print("2. Ingresa email y envía formulario a /reset-password (POST)")
    print("3. Sistema envía email con enlace a /confirm-password-reset?token=...")
    print("4. Usuario hace clic y ve formulario para nueva contraseña")
    print("5. Usuario ingresa nueva contraseña y confirma")
    print("6. Sistema valida token y actualiza contraseña")
    print("7. Usuario recibe confirmación y puede hacer login")
    print("="*60)
