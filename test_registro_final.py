import requests
import json
import logging

# Configuración de logging con más detalle
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# URL del endpoint de registro
url = "http://localhost:8000/user/registro"

# Datos de prueba para el registro
datos_usuario = {
    "nombre": "Usuario Prueba Final2",
    "usuario": "usuario_test_final2",
    "clave": "Contraseña123!",
    "mail": "prueba_final2@example.com",
    "telefono": "+34612345678",
    "acepta_terminos": True
}

def probar_registro():
    logging.info("Enviando solicitud de registro con datos: %s", json.dumps(datos_usuario))
    
    try:
        # Realizar la solicitud POST al endpoint de registro
        respuesta = requests.post(url, json=datos_usuario)
        
        # Obtener el código de estado HTTP y el contenido de la respuesta
        status_code = respuesta.status_code
        contenido = respuesta.json()
        
        logging.info(f"Código de estado: {status_code}")
        logging.info(f"Respuesta: {json.dumps(contenido)}")
        
        # Verificar si el registro fue exitoso
        if status_code == 201:
            logging.info("Registro exitoso!")
            return True
        else:
            logging.error(f"Error en el registro: {contenido}")
            return False
            
    except Exception as e:
        logging.error(f"Error durante la solicitud: {str(e)}")
        return False

if __name__ == "__main__":
    resultado = probar_registro()
    logging.info(f"Resultado final: {'Éxito' if resultado else 'Fallo'}")
