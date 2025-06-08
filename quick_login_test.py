import requests
import json

try:
    print("Probando POST /login...")
    response = requests.post(
        "http://localhost:8001/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 405:
        print("✅ ¡ÉXITO! El login endpoint funciona!")
        print(f"Response: {response.text[:200]}")
    else:
        print("❌ Aún devuelve 405")
        
except Exception as e:
    print(f"Error: {e}")
