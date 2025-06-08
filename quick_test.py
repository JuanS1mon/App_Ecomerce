import requests

# Realizar login rápido
login_response = requests.post('http://127.0.0.1:8000/login', data={'username': 'testuser', 'password': 'Test123456'})
print(f"Login: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json().get('access_token')
    
    # Probar admin
    admin_response = requests.get('http://127.0.0.1:8000/admin', headers={'Authorization': f'Bearer {token}'})
    print(f"Admin: {admin_response.status_code}")
    
    if admin_response.status_code == 200:
        print("✅ ¡ÉXITO! El endpoint /admin funciona correctamente")
        print(f"Tamaño de respuesta: {len(admin_response.content)} bytes")
    else:
        print(f"Error: {admin_response.text[:200]}")
