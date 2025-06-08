"""
Test del nuevo endpoint /cerrar-sesion para verificar si funciona correctamente
"""
import requests
import sys

def test_cerrar_sesion():
    base_url = "http://localhost:8000"
    
    print("=== TEST DEL ENDPOINT /cerrar-sesion ===")
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Intentar hacer logout sin estar logueado
        print("\n1. Test POST /cerrar-sesion sin login previo:")
        response = session.post(f"{base_url}/cerrar-sesion")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.text:
            print(f"Content: {response.text[:200]}")
            
        # 2. Verificar métodos permitidos si es 405
        if response.status_code == 405:
            print(f"Allow header: {response.headers.get('Allow', 'No Allow header')}")
            
        # 3. Probar con OPTIONS para ver qué métodos están disponibles
        print("\n2. Test OPTIONS /cerrar-sesion:")
        options_response = session.options(f"{base_url}/cerrar-sesion")
        print(f"Status: {options_response.status_code}")
        print(f"Allow: {options_response.headers.get('Allow', 'No Allow header')}")
        
        # 4. Probar con GET para comparar
        print("\n3. Test GET /cerrar-sesion:")
        get_response = session.get(f"{base_url}/cerrar-sesion")
        print(f"Status: {get_response.status_code}")
        print(f"Allow: {get_response.headers.get('Allow', 'No Allow header')}")
        
        # 5. Probar login primero y luego logout
        print("\n4. Test completo login -> logout:")
        
        # Intentar login (probablemente falle sin credenciales válidas)
        login_response = session.post(f"{base_url}/login", data={
            "username": "test_user",
            "password": "test_password"
        })
        print(f"Login Status: {login_response.status_code}")
        
        # Hacer logout después
        logout_response = session.post(f"{base_url}/cerrar-sesion")
        print(f"Logout Status: {logout_response.status_code}")
        print(f"Logout Content: {logout_response.text[:200] if logout_response.text else 'No content'}")
        
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor. ¿Está ejecutándose en localhost:8000?")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_cerrar_sesion()
