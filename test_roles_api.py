#!/usr/bin/env python3
"""Script para probar las APIs de roles corregidas"""

import requests
import json

def test_roles_endpoints():
    """Probar los endpoints de roles"""
    base_url = "http://localhost:8000"
    
    # Primero necesitamos un token válido. Para pruebas, usamos el usuario juan
    print("🔐 === OBTENIENDO TOKEN DE AUTENTICACIÓN ===")
    
    login_data = {
        "username": "juan",
        "password": "123456"  # Asumiendo que esta es la contraseña
    }
    
    try:
        # Login para obtener token
        login_response = requests.post(f"{base_url}/token", data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Token obtenido: {token[:50]}...")
            
            # Probar endpoint de roles
            print("\n🏷️ === PROBANDO ENDPOINT DE ROLES ===")
            roles_response = requests.get(
                f"{base_url}/usuarios_admin/roles/",
                params={"token": token}
            )
            print(f"Roles Status: {roles_response.status_code}")
            
            if roles_response.status_code == 200:
                roles = roles_response.json()
                print(f"✅ Roles obtenidos: {len(roles)} roles")
                for rol in roles:
                    print(f"  - {rol['nombre']}: {rol['descripcion']} ({rol['usuarios_count']} usuarios)")
            else:
                print(f"❌ Error obteniendo roles: {roles_response.text}")
            
            # Probar endpoint de usuarios con detalles
            print("\n👥 === PROBANDO ENDPOINT DE USUARIOS CON DETALLES ===")
            usuarios_response = requests.get(
                f"{base_url}/usuarios_admin/usuarios-con-detalles/",
                params={"token": token}
            )
            print(f"Usuarios Status: {usuarios_response.status_code}")
            
            if usuarios_response.status_code == 200:
                usuarios = usuarios_response.json()
                print(f"✅ Usuarios obtenidos: {len(usuarios)} usuarios")
                for usuario in usuarios:
                    print(f"  - {usuario['usuario']} ({usuario['nombre']}): roles {usuario['roles']}")
            else:
                print(f"❌ Error obteniendo usuarios: {usuarios_response.text}")
            
            # Probar creación de rol
            print("\n🆕 === PROBANDO CREACIÓN DE ROL ===")
            nuevo_rol_data = {
                "nombre": "test_rol",
                "descripcion": "Rol de prueba creado por script"
            }
            
            crear_rol_response = requests.post(
                f"{base_url}/usuarios_admin/roles/",
                data=nuevo_rol_data,
                params={"token": token}
            )
            print(f"Crear Rol Status: {crear_rol_response.status_code}")
            
            if crear_rol_response.status_code == 200:
                resultado = crear_rol_response.json()
                print(f"✅ Resultado: {resultado}")
            else:
                print(f"❌ Error creando rol: {crear_rol_response.text}")
                
        else:
            print(f"❌ Error en login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

if __name__ == "__main__":
    test_roles_endpoints()