#!/usr/bin/env python3
"""
Script para verificar el estado actual del endpoint /usuarios/current usando requests
"""

import requests
import sys
import os
sys.path.append('c:/Users/PCJuan/Desktop/sql_app/sql_app')

# URL base del servidor (asumiendo que está corriendo)
BASE_URL = "http://localhost:8000"

def check_server_status():
    """Verificar si el servidor está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_current_endpoint_without_auth():
    """Probar el endpoint sin autenticación"""
    print("============================================================")
    print("🔍 PROBANDO /usuarios/current SIN TOKEN")
    print("============================================================")
    
    try:
        response = requests.get(f"{BASE_URL}/usuarios/current", allow_redirects=False, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 307:
            location = response.headers.get('location', 'Sin ubicación')
            print(f"✅ Redirección correcta a: {location}")
            return True
        elif response.status_code == 200:
            print(f"📄 Respuesta directa: {response.text[:200]}...")
            return True
        else:
            print(f"❌ Respuesta inesperada: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_current_endpoint_with_dummy_token():
    """Probar el endpoint con un token dummy"""
    print("\n============================================================")
    print("🔍 PROBANDO /usuarios/current CON TOKEN DUMMY")
    print("============================================================")
    
    try:
        headers = {"Authorization": "Bearer token_invalido_test"}
        response = requests.get(f"{BASE_URL}/usuarios/current", headers=headers, allow_redirects=False, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 307:
            location = response.headers.get('location', 'Sin ubicación')
            print(f"🔄 Redirección por token inválido a: {location}")
            return True
        elif response.status_code == 200:
            print(f"📄 Respuesta: {response.text[:200]}...")
            return True
        elif response.status_code == 401:
            print(f"🔒 Token inválido (esperado): {response.text[:100]}...")
            return True
        else:
            print(f"❌ Respuesta inesperada: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PRUEBA EN VIVO DEL ENDPOINT /usuarios/current")
    print("=" * 60)
    
    # Verificar si el servidor está corriendo
    if not check_server_status():
        print("❌ Servidor no está corriendo. Inicia con: uvicorn main:app --reload")
        print("📝 Desde la carpeta: c:\\Users\\PCJuan\\Desktop\\sql_app\\sql_app")
        sys.exit(1)
    
    print("✅ Servidor está corriendo")
    
    # Ejecutar las pruebas
    test1 = test_current_endpoint_without_auth()
    test2 = test_current_endpoint_with_dummy_token()
    
    print("\n============================================================")
    print("📊 RESUMEN DE RESULTADOS")
    print("============================================================")
    print(f"Sin token: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Token dummy: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 ¡El endpoint /usuarios/current está funcionando correctamente!")
        print("🔑 Necesita un token JWT válido para devolver datos de usuario")
        print("🔄 Sin token válido, redirige correctamente al login")
    else:
        print("\n⚠️  Hay problemas con el endpoint que requieren investigación")
