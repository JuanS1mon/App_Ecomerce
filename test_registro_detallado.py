import requests
import json
import logging

# Configuración de logging detallada
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# URL del endpoint de registro
url = "http://localhost:8000/user/registro"

# Datos de prueba para el registro
datos_usuario = {
    "nombre": "Usuario Prueba Detallado",
    "usuario": "usuario_test_detallado",
    "clave": "Contraseña123!",
    "mail": "detallado@example.com",
    "telefono": "+34612345679",
    "acepta_terminos": True
}

def probar_registro_con_detalles():
    logging.info("Iniciando prueba de registro detallada")
    logging.debug("Enviando solicitud de registro con datos: %s", json.dumps(datos_usuario))
    
    try:
        # Realizar la solicitud POST al endpoint de registro con respuesta detallada
        respuesta = requests.post(url, json=datos_usuario)
        
        # Obtener el código de estado HTTP y el contenido de la respuesta
        status_code = respuesta.status_code
        contenido = respuesta.json() if respuesta.text else {}
        
        logging.info(f"Código de estado: {status_code}")
        logging.debug(f"Encabezados de respuesta: {respuesta.headers}")
        logging.info(f"Respuesta: {json.dumps(contenido)}")
        
        # Verificar si el registro fue exitoso
        if status_code == 201 or status_code == 200:
            logging.info("Registro procesado con status code: %s", status_code)
            return True
        else:
            logging.error(f"Error en el registro: {contenido}")
            return False
            
    except Exception as e:
        logging.error(f"Error durante la solicitud: {str(e)}")
        return False

if __name__ == "__main__":
    resultado = probar_registro_con_detalles()
    logging.info(f"Resultado final: {'Éxito' if resultado else 'Fallo'}")
