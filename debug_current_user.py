#!/usr/bin/env python3
"""
Debug detallado del endpoint /usuarios/current
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

def debug_current_user_endpoint():
    """Debug del endpoint /usuarios/current"""
    
    # Paso 1: Login
    print("1️⃣ Realizando login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/login",
        data=login_data,
        headers=HEADERS
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login falló: {login_response.status_code}")
        return
    
    response_data = login_response.json()
    token = response_data.get("access_token")
    print(f"✅ Token obtenido: {token[:50]}...")
    
    # Paso 2: Probar /usuarios/current con headers detallados
    print("\n2️⃣ Probando /usuarios/current...")
    auth_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 Headers: {auth_headers}")
    
    try:
        current_user_response = requests.get(
            f"{BASE_URL}/usuarios/current",
            headers=auth_headers
        )
        
        print(f"📋 Status: {current_user_response.status_code}")
        print(f"📋 Headers response: {dict(current_user_response.headers)}")
        
        if current_user_response.status_code == 200:
            user_data = current_user_response.json()
            print(f"📦 Response data: {json.dumps(user_data, indent=2)}")
        else:
            print(f"❌ Error response: {current_user_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Paso 3: Probar sin token para comparar
    print("\n3️⃣ Probando /usuarios/current SIN token...")
    try:
        no_token_response = requests.get(f"{BASE_URL}/usuarios/current")
        print(f"📋 Status sin token: {no_token_response.status_code}")
        if no_token_response.status_code == 200:
            print(f"📦 Data sin token: {json.dumps(no_token_response.json(), indent=2)}")
        else:
            print(f"❌ Error sin token: {no_token_response.text}")
    except Exception as e:
        print(f"❌ Exception sin token: {str(e)}")

if __name__ == "__main__":
    debug_current_user_endpoint()
