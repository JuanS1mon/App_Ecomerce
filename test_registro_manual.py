"""
Script para probar manualmente el endpoint de registro y verificar el error 422
"""
import requests
import json

# URL del servidor
BASE_URL = "http://127.0.0.1:8000"

def probar_registro():
    """Prueba el endpoint de registro con un ejemplo simple"""
    print("Probando endpoint /user/registro...")
    
    # Datos de prueba con acepta_terminos
    datos_usuario = {
        "nombre": "Usuario Prueba",
        "usuario": "usuario_prueba",
        "clave": "Clave123!",
        "mail": "prueba@ejemplo.com",
        "telefono": "+5491122334455",
        "acepta_terminos": True  # Explícitamente como booleano True
    }
    
    # Imprimir datos que enviaremos
    print(f"\nDatos a enviar: {json.dumps(datos_usuario, indent=2)}")
    
    try:
        # Enviar solicitud POST al endpoint de registro
        response = requests.post(
            f"{BASE_URL}/user/registro",
            json=datos_usuario,
            headers={"Content-Type": "application/json"}
        )
        
        # Mostrar detalles de la respuesta
        print(f"\nCódigo de respuesta: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Intentar obtener JSON de la respuesta
        try:
            respuesta_json = response.json()
            print(f"\nRespuesta JSON: {json.dumps(respuesta_json, indent=2)}")
            
            # Si es un error 422, mostrar detalles adicionales
            if response.status_code == 422 and "detail" in respuesta_json:
                print("\n=== DETALLES DEL ERROR 422 ===")
                if isinstance(respuesta_json["detail"], list):
                    for error in respuesta_json["detail"]:
                        campo = error.get("loc", ["unknown"])[-1]
                        mensaje = error.get("msg", "Error desconocido")
                        tipo = error.get("type", "unknown")
                        print(f"Campo: {campo}, Error: {mensaje}, Tipo: {tipo}")
                else:
                    print(f"Error: {respuesta_json['detail']}")
        except ValueError:
            print(f"\nRespuesta no es JSON: {response.text}")
            
    except Exception as e:
        print(f"Error al realizar la solicitud: {str(e)}")

if __name__ == "__main__":
    # Verificar que el servidor esté disponible
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ Servidor disponible en {BASE_URL}")
            probar_registro()
        else:
            print(f"⚠️ El servidor respondió con código {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {str(e)}")
        print("Asegúrate de que el servidor FastAPI esté en ejecución en el puerto 8000")
