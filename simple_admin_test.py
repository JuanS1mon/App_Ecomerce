import requests
import sys

def test_admin():
    # Login
    print("🔐 Realizando login...")
    login_response = requests.post('http://127.0.0.1:8000/login', 
                                 data={'username': 'testuser', 'password': 'Test123456'})
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        return False
    
    token = login_response.json().get('access_token')
    print(f"✅ Login exitoso, token: {token[:30]}...")
    
    # Test admin
    print("🔧 Probando endpoint /admin...")
    headers = {'Authorization': f'Bearer {token}'}
    admin_response = requests.get('http://127.0.0.1:8000/admin', headers=headers)
    
    print(f"Status: {admin_response.status_code}")
    
    if admin_response.status_code == 200:
        print("✅ ¡ÉXITO! El endpoint /admin funciona!")
        print(f"Content-Type: {admin_response.headers.get('content-type')}")
        print(f"Tamaño: {len(admin_response.content)} bytes")
        return True
    else:
        print(f"❌ Error: {admin_response.text[:200]}")
        return False

if __name__ == "__main__":
    test_admin()
