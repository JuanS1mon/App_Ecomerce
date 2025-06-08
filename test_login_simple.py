#!/usr/bin/env python3
import requests
import json

def test_login():
    base_url = 'http://localhost:8000'
    login_data = {'username': 'juan', 'password': '123456'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(f'{base_url}/login', data=login_data, headers=headers, timeout=10)
        print(f'Status: {response.status_code}')
        print(f'Content-Type: {response.headers.get("Content-Type", "N/A")}')
        
        if 'application/json' in response.headers.get('Content-Type', ''):
            print(f'JSON Response: {json.dumps(response.json(), indent=2)}')
        else:
            print(f'Response: {response.text[:500]}...')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_login()
