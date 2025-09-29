#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el login del usuario juan correctamente con form data
"""

import requests

def test_juan_login_form():
    """Prueba el login de juan usando form data como lo haría un navegador"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("=== PRUEBA DE LOGIN CON FORM DATA ===")
    
    try:
        # Datos del formulario
        form_data = {
            "username": "juan",
            "password": "admin123",
            "next": "/usuarios_admin/"
        }
        
        # Headers que simularían un navegador web
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        print("1. Enviando login con form data...")
        print(f"   Form data: {form_data}")
        print(f"   Headers: {headers}")
        
        response = requests.post(
            f"{base_url}/auth/login", 
            data=form_data,
            headers=headers,
            allow_redirects=False  # No seguir redirects automáticamente
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers response: {dict(response.headers)}")
        
        # Revisar cookies
        if response.cookies:
            print(f"   Cookies: {dict(response.cookies)}")
            
        if response.status_code == 303:
            print("   ✅ Login exitoso! (Redirect detectado)")
            redirect_url = response.headers.get('Location', '')
            print(f"   🔄 Redirect a: {redirect_url}")
            
            # Seguir el redirect manualmente para ver si funciona
            if redirect_url:
                if not redirect_url.startswith('http'):
                    redirect_url = base_url + redirect_url
                
                print(f"2. Siguiendo redirect a: {redirect_url}")
                
                # Usar las cookies del login
                cookies = response.cookies
                follow_response = requests.get(redirect_url, cookies=cookies)
                
                print(f"   Status Code del redirect: {follow_response.status_code}")
                
                if follow_response.status_code == 200:
                    print("   ✅ ¡Acceso a usuarios_admin exitoso!")
                    print("   🎉 El usuario 'juan' tiene permisos correctos")
                    
                    # Verificar si el contenido contiene elementos típicos de admin
                    content = follow_response.text.lower()
                    if "administraci" in content or "usuarios" in content or "admin" in content:
                        print("   ✅ Página de administración confirmada")
                    else:
                        print("   ⚠️  Página cargada pero podría no ser la de admin")
                        
                else:
                    print(f"   ❌ Error siguiendo redirect: {follow_response.status_code}")
                    print(f"   Response: {follow_response.text[:200]}...")
                    
        elif response.status_code == 200:
            print("   ✅ Login exitoso! (Respuesta directa)")
            # Buscar token en la respuesta
            try:
                json_resp = response.json()
                if 'access_token' in json_resp:
                    token = json_resp['access_token']
                    print(f"   🔑 Token obtenido: {token[:50]}...")
            except:
                print("   ℹ️  Respuesta no es JSON")
                
        else:
            print(f"   ❌ Login falló: {response.status_code}")
            print(f"   Response: {response.text[:300]}...")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión. ¿Está el servidor ejecutándose?")
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_juan_login_form()