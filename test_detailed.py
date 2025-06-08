import requests
import json

def test_detailed():
    base_url = "http://localhost:8000"
    
    print("🧪 Probando endpoint raíz con más detalle...")
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content Length: {len(response.text)}")
        print(f"Content: {response.text}")
    except Exception as e:
        print(f"Error al hacer request: {e}")

if __name__ == "__main__":
    test_detailed()
