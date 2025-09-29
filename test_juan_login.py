#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el login del usuario juan y acceder a usuarios_admin
"""

import requests
import json

def test_juan_login_and_admin_access():
    """Prueba el login de juan y el acceso a usuarios_admin"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("=== PRUEBA DE LOGIN Y ACCESO ADMIN ===")
    
    try:
        # 1. Hacer login
        print("1. Intentando hacer login con usuario 'juan'...")
        
        login_data = {
            "username": "juan",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Login exitoso!")
            
            # Buscar el token en la respuesta
            token = None
            
            # Buscar en cookies
            if 'access_token' in response.cookies:
                token = response.cookies['access_token']
                print(f"   🍪 Token encontrado en cookies: {token[:50]}...")
            
            # Buscar en JSON response
            try:
                json_response = response.json()
                if 'access_token' in json_response:
                    token = json_response['access_token']
                    print(f"   📄 Token encontrado en JSON: {token[:50]}...")
                print(f"   📄 Respuesta completa: {json_response}")
            except:
                pass
            
            # Buscar en headers
            if 'Authorization' in response.headers:
                token = response.headers['Authorization'].replace('Bearer ', '')
                print(f"   📋 Token encontrado en headers: {token[:50]}...")
            
            if token:
                print(f"   🔑 Token obtenido exitosamente")
                
                # 2. Intentar acceder a usuarios_admin con el token
                print("2. Intentando acceder a /usuarios_admin/ con token...")
                
                # Método 1: Token en query parameter
                admin_response = requests.get(f"{base_url}/usuarios_admin/?token={token}")
                print(f"   📡 Respuesta con token en query: {admin_response.status_code}")
                
                if admin_response.status_code == 200:
                    print("   ✅ ¡Acceso a usuarios_admin exitoso!")
                    print("   🎉 El usuario 'juan' tiene permisos de administrador correctos")
                else:
                    print(f"   ❌ Error accediendo a usuarios_admin: {admin_response.status_code}")
                    print(f"   📄 Error details: {admin_response.text[:200]}...")
                
                # Método 2: Token en header Authorization
                headers = {"Authorization": f"Bearer {token}"}
                admin_response2 = requests.get(f"{base_url}/usuarios_admin/", headers=headers)
                print(f"   📡 Respuesta con token en header: {admin_response2.status_code}")
                
            else:
                print("   ❌ No se pudo obtener el token de acceso")
                
        elif response.status_code == 302:
            print("   🔄 Redirect detectado")
            print(f"   📍 Location: {response.headers.get('Location', 'No location header')}")
            
            # Seguir el redirect si existe
            if 'Location' in response.headers:
                redirect_url = response.headers['Location']
                if not redirect_url.startswith('http'):
                    redirect_url = base_url + redirect_url
                print(f"   🔄 Siguiendo redirect a: {redirect_url}")
                
                redirect_response = requests.get(redirect_url)
                print(f"   📡 Respuesta del redirect: {redirect_response.status_code}")
                
        else:
            print(f"   ❌ Login falló: {response.status_code}")
            print(f"   📄 Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión. ¿Está el servidor ejecutándose en http://127.0.0.1:8000?")
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_juan_login_and_admin_access()