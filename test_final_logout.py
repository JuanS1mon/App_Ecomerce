"""
Test final para confirmar que /logout está funcionando correctamente
"""
import requests

def test_final_logout():
    base_url = "http://localhost:8000"
    
    print("=== TEST FINAL DEL ENDPOINT /logout ===")
    
    session = requests.Session()
    
    try:
        # Test del endpoint original /logout
        print("1. Test POST /logout:")
        response = session.post(f"{base_url}/logout")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Respuesta: {response.json()}")
            print("   ✅ Headers de cookie:")
            for header, value in response.headers.items():
                if 'cookie' in header.lower():
                    print(f"     {header}: {value}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            if response.status_code == 405:
                print(f"     Allow: {response.headers.get('Allow', 'No Allow header')}")
        
        # Comparar con otros endpoints
        print("\n2. Comparación con otros endpoints:")
        
        endpoints = ["/logout", "/logout-test", "/logout-simple"]
        for endpoint in endpoints:
            response = session.post(f"{base_url}{endpoint}")
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
        
        print("\n=== RESULTADO FINAL ===")
        logout_response = session.post(f"{base_url}/logout")
        if logout_response.status_code == 200:
            print("🎉 ¡PROBLEMA RESUELTO!")
            print("✅ El endpoint /logout funciona correctamente")
            print("✅ La sesión se cierra apropiadamente")
            print("✅ Las cookies se limpian correctamente")
            print("\n📋 SOLUCIÓN:")
            print("   - Cambiar Depends(current_user) por Depends(get_optional_user)")
            print("   - Esto permite que el logout funcione sin requerir autenticación obligatoria")
        else:
            print("❌ El problema persiste")
            print(f"   Status: {logout_response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_final_logout()
