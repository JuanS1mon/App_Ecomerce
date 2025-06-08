# -*- coding: utf-8 -*-
"""
Prueba simple del flujo de reset de contraseña - Verificación manual
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_email_request():
    """
    Prueba enviar solicitud de reset por email
    """
    print("📧 Enviando solicitud de reset por email...")
    
    # Usar un email real para recibir el correo
    email = "fjuansimon@gmail.com"  # Cambia por tu email
    
    reset_data = {"email": email}
    
    try:
        response = requests.post(f"{BASE_URL}/password-reset-request", 
                               json=reset_data, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Solicitud enviada correctamente")
            print("\n📬 REVISA TU CORREO ELECTRÓNICO")
            print("Busca un correo con:")
            print("- Asunto: 'Restablecimiento de contraseña'")
            print("- Enlace que comienza con: http://localhost:8000/confirm-password-reset?token=...")
            print("\n🔗 Al hacer clic en el enlace deberías ver:")
            print("1. Una página moderna con formulario para nueva contraseña")
            print("2. Indicador de fortaleza de contraseña")
            print("3. Validación de contraseñas coincidentes")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pages_accessibility():
    """
    Verifica que las páginas sean accesibles
    """
    print("\n🌐 Verificando accesibilidad de páginas...")
    
    pages = [
        ("/reset-password", "Página de solicitud de reset"),
        ("/confirm-password-reset", "Página de confirmación de reset")
    ]
    
    for path, description in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} - OK")
            else:
                print(f"❌ {description} - Error {response.status_code}")
        except Exception as e:
            print(f"❌ {description} - Error: {e}")

def test_token_validation():
    """
    Prueba la validación de tokens inválidos
    """
    print("\n🧪 Probando validación de tokens...")
    
    invalid_tokens = [
        "token.invalido.test",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.token",
        "",
        "abc123"
    ]
    
    for token in invalid_tokens:
        print(f"\nProbando token: {token[:20]}...")
        
        confirm_data = {
            "token": token,
            "new_password": "test123",
            "confirm_password": "test123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/confirm-password-reset", 
                                   json=confirm_data, timeout=10)
            
            if response.status_code == 400:
                print("✅ Token inválido rechazado correctamente")
            else:
                print(f"⚠️ Respuesta inesperada: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def show_flow_summary():
    """
    Muestra un resumen del flujo corregido
    """
    print("\n" + "="*60)
    print("🔄 FLUJO DE RESET DE CONTRASEÑA CORREGIDO")
    print("="*60)
    print("PROBLEMA ANTERIOR:")
    print("  ❌ El enlace del correo llevaba a /reset-password")
    print("  ❌ Era la misma página para solicitar reset")
    print("  ❌ No había formulario para ingresar nueva contraseña")
    print("")
    print("SOLUCIÓN IMPLEMENTADA:")
    print("  ✅ Nuevo endpoint: /confirm-password-reset")
    print("  ✅ Nueva página: confirm_password_reset.html")
    print("  ✅ El enlace del correo ahora lleva a la página correcta")
    print("  ✅ Formulario específico para cambiar contraseña")
    print("")
    print("ENDPOINTS ACTUALES:")
    print("  📄 GET  /reset-password          → Página para solicitar reset")
    print("  📨 POST /password-reset-request  → Envía email con enlace")
    print("  📄 GET  /confirm-password-reset  → Página para cambiar contraseña")
    print("  💾 POST /confirm-password-reset  → Procesa nueva contraseña")
    print("")
    print("FLUJO CORRECTO:")
    print("  1. Usuario va a /reset-password")
    print("  2. Ingresa email y solicita reset")
    print("  3. Recibe email con enlace a /confirm-password-reset?token=...")
    print("  4. Hace clic y ve formulario para nueva contraseña")
    print("  5. Ingresa nueva contraseña y confirma")
    print("  6. Sistema actualiza contraseña en BD")
    print("  7. Usuario puede hacer login con nueva contraseña")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Verificación del flujo de reset de contraseña corregido...")
    
    # Verificar servidor
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Servidor funcionando")
    except Exception:
        print("❌ Servidor no accesible")
        print("Ejecuta: uvicorn sql_app.main:app --reload")
        exit(1)
    
    # Ejecutar pruebas
    test_pages_accessibility()
    test_token_validation()
    test_email_request()
    show_flow_summary()
    
    print("\n✅ Verificación completada!")
    print("📧 ACCIÓN REQUERIDA: Revisa tu correo electrónico para probar el enlace real")
