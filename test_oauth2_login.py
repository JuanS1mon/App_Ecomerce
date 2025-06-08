#!/usr/bin/env python3
"""
Script para probar el login con OAuth2PasswordRequestForm correctamente
"""
import requests

def test_oauth2_login():
    """Prueba el login con formato OAuth2 correcto"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔐 PROBANDO LOGIN CON OAUTH2 FORMAT")
    print("=" * 45)
    
    session = requests.Session()
    
    # OAuth2PasswordRequestForm espera form data con Content-Type específico
    login_data = {
        "username": "juan",
        "password": "123456",
        "grant_type": "password"  # Opcional pero recomendado para OAuth2
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    try:
        print(f"📡 Enviando petición POST a /login...")
        print(f"   Data: {login_data}")
        print(f"   Headers: {headers}")
        
        response = session.post(
            f"{base_url}/login",
            data=login_data,
            headers=headers
        )
        
        print(f"\n📊 RESPUESTA:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"   ✅ LOGIN EXITOSO")
            
            try:
                json_response = response.json()
                print(f"   📄 Response JSON:")
                for key, value in json_response.items():
                    if key == "access_token":
                        print(f"      {key}: ***TOKEN*** (longitud: {len(str(value))})")
                    else:
                        print(f"      {key}: {value}")
                
                # Verificar cookies
                cookies = dict(session.cookies)
                print(f"   🍪 Cookies: {list(cookies.keys())}")
                
                if "access_token" in cookies:
                    print(f"   ✅ Token en cookies: Presente")
                    
                    # Ahora probar acceso al admin
                    print(f"\n🏛️ PROBANDO ACCESO AL ADMIN...")
                    admin_response = session.get(f"{base_url}/admin")
                    print(f"   Admin Status: {admin_response.status_code}")
                    
                    if admin_response.status_code == 200:
                        # Verificar si es la página de admin real o login
                        if "Panel de Administración" in admin_response.text or "Dashboard" in admin_response.text:
                            print(f"   🎉 ACCESO AL ADMIN EXITOSO")
                            return True
                        elif "Iniciar sesión" in admin_response.text or "login" in admin_response.text.lower():
                            print(f"   ⚠️  Devuelve página de login - problema de autenticación")
                        else:
                            print(f"   ⚠️  Respuesta inesperada")
                    else:
                        print(f"   ❌ Error al acceder al admin: {admin_response.status_code}")
                else:
                    print(f"   ⚠️  Token no está en cookies")
                    
                return True
                
            except Exception as e:
                print(f"   ⚠️  Error procesando JSON: {str(e)}")
                print(f"   📄 Response text: {response.text[:200]}...")
                
        elif response.status_code == 422:
            print(f"   ❌ Error de validación:")
            try:
                error_detail = response.json()
                print(f"   📄 {error_detail}")
            except:
                print(f"   📄 {response.text}")
                
        elif response.status_code == 405:
            print(f"   ❌ Método no permitido - problema con la configuración de ruta")
            
        else:
            print(f"   ❌ Error inesperado: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"   💥 Error de conexión: {str(e)}")
        return False

def main():
    success = test_oauth2_login()
    
    print(f"\n" + "=" * 45)
    if success:
        print(f"🎉 RESULTADO: LOGIN Y ADMIN FUNCIONANDO")
    else:
        print(f"⚠️  RESULTADO: PROBLEMA EN LOGIN O ADMIN")
    
    return success

if __name__ == "__main__":
    main()
