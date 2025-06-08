"""
Script para probar el endpoint de registro y verificar el error 422
"""
import requests
import json

# URL del servidor
BASE_URL = "http://127.0.0.1:8000"

def test_register_user():
    """Prueba el endpoint de registro con diferentes datos"""
    
    # Caso 1: Datos básicos que deberían funcionar
    user_data_basic = {
        "nombre": "Juan Pérez",
        "usuario": "juan.perez",
        "clave": "MiPassword123!",
        "mail": "juan.perez@email.com"
    }
    
    # Caso 2: Contraseña que NO cumple requisitos
    user_data_weak_password = {
        "nombre": "Ana García",
        "usuario": "ana.garcia",
        "clave": "123",  # Muy débil
        "mail": "ana.garcia@email.com"
    }
    
    # Caso 3: Email inválido
    user_data_invalid_email = {
        "nombre": "Carlos López",
        "usuario": "carlos.lopez",
        "clave": "MiPassword123!",
        "mail": "email-invalido"
    }
    
    # Caso 4: Campos faltantes
    user_data_missing_fields = {
        "nombre": "Pedro Martín",
        "usuario": "pedro.martin"
        # Faltan clave y mail
    }
    
    test_cases = [
        ("Datos válidos", user_data_basic),
        ("Contraseña débil", user_data_weak_password),
        ("Email inválido", user_data_invalid_email),
        ("Campos faltantes", user_data_missing_fields)
    ]
    
    for test_name, data in test_cases:
        print(f"\n=== PRUEBA: {test_name} ===")
        print(f"Datos enviados: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/user/registro",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Registro exitoso")
                print(f"Respuesta: {response.json()}")
            else:
                print(f"❌ Error en registro")
                try:
                    error_detail = response.json()
                    print(f"Detalle del error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"Respuesta de error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose?")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")

def test_password_requirements():
    """Prueba específica para ver los requisitos de contraseña"""
    print("\n=== PRUEBA DE REQUISITOS DE CONTRASEÑA ===")
    
    passwords = [
        "123",           # Muy corta
        "password",      # Sin mayúsculas, números o símbolos
        "Password",      # Sin números o símbolos
        "Password1",     # Sin símbolos
        "Password1!",    # Debería ser válida
        "MiContraseña123!",  # Debería ser válida
    ]
    
    base_user = {
        "nombre": "Test User",
        "usuario": "test.user",
        "mail": "test@email.com"
    }
    
    for i, password in enumerate(passwords, 1):
        print(f"\nPrueba {i}: '{password}'")
        
        user_data = base_user.copy()
        user_data["clave"] = password
        
        try:
            response = requests.post(
                f"{BASE_URL}/user/registro",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Contraseña aceptada")
            elif response.status_code == 422:
                try:
                    error = response.json()
                    if isinstance(error.get("detail"), dict):
                        print(f"❌ Validación Pydantic: {error['detail'].get('message', 'Error de validación')}")
                    else:
                        print(f"❌ Error 422: {error.get('detail', 'Error de validación')}")
                except:
                    print(f"❌ Error 422: {response.text}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔍 PROBANDO ENDPOINT DE REGISTRO DE USUARIOS")
    print("=" * 50)
    
    # Verificar que el servidor esté disponible
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Servidor disponible (código: {response.status_code})")
    except:
        print("❌ Servidor no disponible. Asegúrate de que esté ejecutándose en el puerto 8000")
        exit(1)
    
    test_register_user()
    test_password_requirements()
    
    print("\n" + "=" * 50)
    print("🏁 PRUEBAS COMPLETADAS")
