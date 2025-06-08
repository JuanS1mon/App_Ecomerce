#!/usr/bin/env python3
"""
Script para investigar los roles del usuario admin en el token
"""

import requests
import jwt
import json

def investigate_admin_token():
    """Investiga el contenido del token del usuario admin"""
    base_url = "http://localhost:8001"
    
    print("🔍 INVESTIGANDO TOKEN DEL USUARIO ADMIN")
    print("=" * 50)
    
    # Paso 1: Login
    print("\n1. Realizando login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = requests.post(
        f"{base_url}/login",
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    print(f"   Status del login: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Error en login: {login_response.text}")
        return
    
    login_json = login_response.json()
    token = login_json.get('access_token')
    
    print("   ✅ Login exitoso")
    print(f"   Token: {token[:30]}...")
    
    # Paso 2: Decodificar token (sin verificar firma para debug)
    print("\n2. Decodificando token...")
    try:
        # Decodificar sin verificar (solo para debug)
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("   📋 Contenido del token:")
        print(json.dumps(decoded, indent=4, ensure_ascii=False))
        
        # Verificar roles específicamente
        roles = decoded.get('roles', [])
        print(f"\n   🎭 Roles en el token: {roles}")
        
        has_admin = 'admin' in roles
        print(f"   🔑 ¿Tiene rol admin?: {has_admin}")
        
    except Exception as e:
        print(f"   ❌ Error decodificando token: {e}")
    
    # Paso 3: Verificar endpoint /usuarios/current
    print("\n3. Verificando /usuarios/current...")
    
    current_response = requests.get(
        f"{base_url}/usuarios/current",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"   Status: {current_response.status_code}")
    
    if current_response.status_code == 200:
        user_data = current_response.json()
        print("   📋 Datos del usuario actual:")
        print(json.dumps(user_data, indent=4, ensure_ascii=False))
        
        # Verificar roles en el endpoint
        roles_from_endpoint = user_data.get('roles', [])
        print(f"\n   🎭 Roles desde endpoint: {roles_from_endpoint}")
        
        # Verificar si tiene admin
        has_admin_endpoint = any(
            (isinstance(role, dict) and role.get('nombre') == 'admin') or role == 'admin'
            for role in roles_from_endpoint
        )
        print(f"   🔑 ¿Tiene rol admin en endpoint?: {has_admin_endpoint}")
        
    else:
        print(f"   ❌ Error: {current_response.text}")
    
    # Paso 4: Probar acceso directo a admin
    print("\n4. Probando acceso a /admin...")
    
    admin_response = requests.get(
        f"{base_url}/admin",
        headers={'Authorization': f'Bearer {token}'},
        allow_redirects=False
    )
    
    print(f"   Status: {admin_response.status_code}")
    
    if admin_response.status_code == 200:
        print("   ✅ ¡Acceso exitoso!")
    elif admin_response.status_code in [301, 302, 307, 308]:
        redirect = admin_response.headers.get('location', 'No location')
        print(f"   🔄 Redirect a: {redirect}")
        
        # Si redirige, verificar por qué
        if 'login' in redirect.lower():
            print("   ❌ Redirige a login - problema de autenticación/autorización")
        else:
            print("   ⚠️  Redirige a otra página")
    else:
        print(f"   ❌ Error: {admin_response.text}")

if __name__ == "__main__":
    investigate_admin_token()
