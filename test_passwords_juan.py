#!/usr/bin/env python3
import requests
import json

def test_different_passwords():
    base_url = 'http://localhost:8000'
    username = 'juan'
    passwords_to_try = ['admin', 'juan', 'password', 'test', '12345678', '123', 'qwerty', '1234', 'juan123']
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    print("🔐 PROBANDO DIFERENTES CONTRASEÑAS PARA JUAN")
    print("=" * 50)
    
    for password in passwords_to_try:
        login_data = {'username': username, 'password': password}
        
        try:
            response = requests.post(f'{base_url}/login', data=login_data, headers=headers, timeout=10)
            print(f'Password "{password}": Status {response.status_code}')
            
            if response.status_code == 200:
                print(f'🎉 ¡CONTRASEÑA CORRECTA ENCONTRADA: {password}!')
                print(f'Response: {response.json()}')
                return password
            elif response.status_code == 307:
                print(f'   → Redirección (posiblemente credenciales incorrectas)')
            elif response.status_code == 401:
                print(f'   → Credenciales incorrectas')
            elif response.status_code == 422:
                print(f'   → Error de validación')
                
        except Exception as e:
            print(f'Password "{password}": Error - {e}')
    
    print('\n❌ No se encontró la contraseña correcta')
    return None

if __name__ == "__main__":
    test_different_passwords()
