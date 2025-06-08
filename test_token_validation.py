import requests
import json

def test_token_validation():
    print("🔧 TESTING TOKEN VALIDATION STEP BY STEP")
    print("=" * 50)
    
    # Paso 1: Login y obtener token
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    print("🔐 Paso 1: Haciendo login...")
    login_response = requests.post(
        "http://localhost:8000/login",
        data=login_data,
        headers=headers
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login falló: {login_response.status_code}")
        return
        
    token_data = login_response.json()
    access_token = token_data.get('access_token')
    
    print(f"✅ Token obtenido: {access_token[:30]}...")
    print(f"📊 Token length: {len(access_token)}")
    
    # Paso 2: Verificar token manualmente usando JWT
    try:
        import jwt
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        SECRET = os.getenv("SECRET")
        ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
        print(f"\n🔧 Paso 2: Verificando token con JWT...")
        print(f"📊 SECRET presente: {bool(SECRET)}")
        print(f"📊 ALGORITHM: {ALGORITHM}")
        
        # Decodificar token
        payload = jwt.decode(access_token, SECRET, algorithms=[ALGORITHM])
        print(f"✅ Token válido!")
        print(f"📊 Payload: {json.dumps(payload, indent=2, default=str)}")
        
    except Exception as e:
        print(f"❌ Error decodificando token: {e}")
        return
    
    # Paso 3: Test diferentes formas de enviar el token
    print(f"\n🔧 Paso 3: Testing diferentes métodos de envío...")
    
    # 3a. Bearer en Authorization header
    print(f"\n🔸 Test A: Bearer token en Authorization header")
    auth_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'TestClient/1.0'
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/admin-debug",
            headers=auth_headers,
            timeout=10
        )
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("❌ 401 - Token rechazado")
        elif response.status_code == 200:
            print("✅ 200 - Token aceptado")
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❓ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en request: {e}")
    
    # 3b. Cookie
    print(f"\n🔸 Test B: Token en cookies")
    
    # Crear session y hacer login para obtener cookies
    session = requests.Session()
    session.post("http://localhost:8000/login", data=login_data, headers=headers)
    
    print(f"📊 Cookies después del login: {list(session.cookies.keys())}")
    
    try:
        response = session.get(
            "http://localhost:8000/admin-debug",
            timeout=10
        )
        print(f"📊 Status con cookies: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ 401 - Cookies rechazadas")
        elif response.status_code == 200:
            print("✅ 200 - Cookies aceptadas")
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❓ Status inesperado con cookies: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error con cookies: {e}")
    
    # Paso 4: Comparar con endpoint que funciona
    print(f"\n🔧 Paso 4: Comparando con /usuarios/current que funciona...")
    
    try:
        response = requests.get(
            "http://localhost:8000/usuarios/current",
            headers=auth_headers,
            timeout=10
        )
        print(f"📊 Current user status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current user funciona: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Current user también falla: {response.status_code}")
            print(f"📊 Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error en current user: {e}")

if __name__ == "__main__":
    test_token_validation()
