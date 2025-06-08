#!/usr/bin/env python3
"""
Script para probar la funcionalidad de reset de contraseña
"""

import requests
import json

def test_reset_password():
    """Probar el endpoint de reset de contraseña"""
    print('🔄 Probando reset de contraseña...')
    
    try:
        response = requests.post('http://localhost:8000/reset-password',
                               data={'username': 'fjuansimon@gmail.com', 'password': 'dummy'},
                               headers={'Content-Type': 'application/x-www-form-urlencoded'},
                               timeout=10)
        
        print(f'Status: {response.status_code}')
        print(f'Headers: {dict(response.headers)}')
        
        if response.status_code == 200:
            try:
                print(f'Respuesta JSON: {response.json()}')
            except:
                print(f'Respuesta texto: {response.text}')
        else:
            print(f'Error: {response.text[:500]}')
            
    except requests.exceptions.Timeout:
        print('❌ Timeout - el servidor tardó demasiado en responder')
    except requests.exceptions.RequestException as e:
        print(f'❌ Error de conexión: {e}')

if __name__ == "__main__":
    test_reset_password()
