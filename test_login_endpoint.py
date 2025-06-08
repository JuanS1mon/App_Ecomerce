#!/usr/bin/env python3
"""
Script para probar el endpoint de login
"""

import requests
import json

def test_login():
    url = "http://localhost:8001/login"
    
    # Datos de prueba para el login
    data = {
        "username": "admin",  # Cambia por un usuario válido
        "password": "admin123"  # Cambia por una contraseña válida
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"🔍 Probando POST {url}")
    print(f"📄 Datos: {data}")
    
    try:
        response = requests.post(url, data=data, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login exitoso!")
            try:
                json_response = response.json()
                print("📄 Respuesta JSON:")
                print(json.dumps(json_response, indent=2))
            except:
                print("📄 Respuesta (texto):")
                print(response.text)
        else:
            print("❌ Error en login")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_login_page():
    url = "http://localhost:8001/loginpage"
    
    print(f"🔍 Probando GET {url}")
    
    try:
        response = requests.get(url)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de login disponible!")
        else:
            print("❌ Página de login no disponible")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBAS DE LOGIN")
    print("=" * 50)
    
    # Probar página de login
    test_login_page()
    print()
    
    # Probar endpoint de login
    test_login()
