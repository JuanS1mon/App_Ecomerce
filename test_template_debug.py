#!/usr/bin/env python3
"""
Script para debuggear el sistema de templates
"""

import os
import requests

def test_template_system():
    """Debuggear el sistema de templates"""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    print("DEBUG: Template System")
    print("=" * 40)
    
    # Verificar archivos localmente
    base_dir = "C:/Users/PCJuan/Desktop/sql_app/sql_app"
    static_dir = f"{base_dir}/static"
    
    print(f"Base dir: {base_dir}")
    print(f"Static dir: {static_dir}")
    print(f"Directory exists: {os.path.exists(static_dir)}")
    
    # Verificar archivos específicos
    files_to_check = [
        "sql_app/static/index.html",
        "sql_app/static/html/admin.html",
        "sql_app/static/login.html"
    ]
    
    for file_path in files_to_check:
        full_path = f"{base_dir}/{file_path}"
        exists = os.path.exists(full_path)
        print(f"File {file_path}: {'EXISTS' if exists else 'NOT FOUND'}")
        if exists:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  - Size: {len(content)} chars")
                    print(f"  - First 100 chars: {content[:100]}...")
            except Exception as e:
                print(f"  - Error reading: {e}")
    
    # Probar login primero
    print(f"\nTesting login...")
    login_data = {'username': 'testuser', 'password': 'Test123456'}
    try:
        login_response = requests.post(f"{BASE_URL}/login", data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print(f"Login successful, token: {token[:30]}...")
            
            # Crear un endpoint simple para probar templates
            print(f"\nTesting template endpoints...")
            headers = {'Authorization': f'Bearer {token}'}
            
            # Probar diferentes endpoints
            endpoints = ['/admin', '/admin-simple']
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    print(f"{endpoint}: Status {resp.status_code}")
                    if resp.status_code == 500:
                        print(f"  Error content: {resp.text[:200]}...")
                except Exception as e:
                    print(f"{endpoint}: Error - {e}")
        else:
            print(f"Login failed: {login_response.status_code}")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_template_system()
