#!/usr/bin/env python3
"""
Script para probar el flujo completo de login y acceso a admin
"""

import requests
import sys

def test_complete_flow():
    """Prueba el flujo completo de autenticación y acceso a admin"""
    base_url = "http://localhost:8001"
    
    print("🔐 PROBANDO FLUJO COMPLETO DE AUTENTICACIÓN")
    print("=" * 60)
    
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
        return False
    
    # Extraer token
    login_json = login_response.json()
    token = login_json.get('access_token')
    
    if not token:
        print("   ❌ No se recibió token de acceso")
        return False
    
    print(f"   ✅ Login exitoso, token recibido: {token[:20]}...")
    
    # Paso 2: Acceder a /admin con token
    print("\n2. Accediendo a /admin con token...")
    
    admin_response = requests.get(
        f"{base_url}/admin",
        headers={'Authorization': f'Bearer {token}'},
        allow_redirects=False  # No seguir redirects automáticamente
    )
    
    print(f"   Status de /admin: {admin_response.status_code}")
    
    if admin_response.status_code == 200:
        print("   ✅ ¡ÉXITO! Acceso a /admin permitido")
        print(f"   📄 Contenido recibido: {len(admin_response.text)} caracteres")
        return True
    elif admin_response.status_code in [301, 302, 307, 308]:
        redirect_location = admin_response.headers.get('location', 'No location')
        print(f"   🔄 Redirect a: {redirect_location}")
        
        # Si es redirect a login, es un problema
        if 'login' in redirect_location.lower():
            print("   ❌ Redirigiendo a login - problema de autenticación")
            return False
        else:
            print("   ⚠️  Redirect a otra página")
            return False
    else:
        print(f"   ❌ Error de acceso: {admin_response.text}")
        return False

    # Paso 3: Verificar información del usuario actual
    print("\n3. Verificando usuario actual...")
    
    current_user_response = requests.get(
        f"{base_url}/usuarios/current",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"   Status de /usuarios/current: {current_user_response.status_code}")
    
    if current_user_response.status_code == 200:
        user_data = current_user_response.json()
        print(f"   ✅ Usuario actual: {user_data.get('usuario', 'No user')}")
        roles = user_data.get('roles', [])
        print(f"   🎭 Roles: {[role.get('nombre', role) if isinstance(role, dict) else role for role in roles]}")
        
        # Verificar si tiene rol admin
        has_admin = any(
            (isinstance(role, dict) and role.get('nombre') == 'admin') or role == 'admin'
            for role in roles
        )
        
        if has_admin:
            print("   ✅ Usuario tiene rol de administrador")
        else:
            print("   ⚠️  Usuario NO tiene rol de administrador")
            
    else:
        print(f"   ❌ Error obteniendo usuario actual: {current_user_response.text}")

if __name__ == "__main__":
    success = test_complete_flow()
    
    if success:
        print("\n🎉 FLUJO DE AUTENTICACIÓN COMPLETADO EXITOSAMENTE")
        print("✅ El problema de login→admin ha sido RESUELTO")
    else:
        print("\n❌ PROBLEMAS DETECTADOS EN EL FLUJO")
        print("🔧 Se requiere investigación adicional")
        
    sys.exit(0 if success else 1)
