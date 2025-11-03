#!/usr/bin/env python3
"""
Test final del registro de usuarios ecommerce
"""
import httpx
import time

def test_registration():
    # Datos de prueba únicos
    user_data = {
        "nombre": "Juan",
        "apellido": "Ferreyra",
        "email": f"juan.ferreyra{int(time.time())}@example.com",  # Email único
        "contraseña": "password123",
        "telefono": "01159002769",
        "direccion": "a",
        "ciudad": "Del Viso",
        "provincia": "pilar",
        "pais": "Argentina"
    }

    print("Intentando registrar usuario...")
    print(f"Datos: {user_data}")

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                "http://localhost:8001/ecommerce/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 201:
                print("✅ ¡Registro exitoso!")
                return True
            elif response.status_code == 400:
                print("❌ Error 400 - Datos inválidos")
                return False
            else:
                print(f"❌ Error {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    time.sleep(3)  # Esperar a que el servidor inicie
    success = test_registration()
    print(f"\nResultado: {'ÉXITO' if success else 'FALLÓ'}")