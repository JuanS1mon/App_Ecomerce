import requests
import json
import logging
from datetime import datetime

# Configurar logging para escribir a un archivo con ruta absoluta
import os
log_dir = "c:\\Users\\PCJuan\\Desktop\\sql_app"
log_filename = os.path.join(log_dir, f"registro_test_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# URL del endpoint de registro
url = "http://localhost:8000/user/registro"

# Datos de prueba para el registro con contraseña correcta
datos_usuario = {
    "nombre": "Juan Simon",
    "usuario": "juansimon",
    "clave": "123", # Contraseña simple que cumple los nuevos requisitos (mínimo 3 caracteres)
    "mail": "fjuansimon@gmail.com",
    "telefono": "+541159002769",
    "acepta_terminos": True
}

def probar_registro_con_log():
    logging.info(f"Iniciando prueba de registro con log (se guardará en {log_filename})")
    logging.info("Enviando solicitud de registro con datos: %s", json.dumps(datos_usuario))
    
    try:
        # Realizar la solicitud POST al endpoint de registro
        respuesta = requests.post(url, json=datos_usuario)
        
        # Guardar todos los detalles de la respuesta con ruta absoluta
        respuesta_file = os.path.join(log_dir, f"respuesta_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(respuesta_file, "w", encoding="utf-8") as f:
            f.write(f"Status Code: {respuesta.status_code}\n")
            f.write(f"Headers: {json.dumps(dict(respuesta.headers))}\n")
            f.write(f"Contenido: {respuesta.text}\n")
        
        # Registrar información en el log
        logging.info(f"Código de estado: {respuesta.status_code}")
        logging.info(f"Encabezados: {json.dumps(dict(respuesta.headers))}")
        logging.info(f"Contenido: {respuesta.text}")
        
        return respuesta.status_code in (200, 201)
            
    except Exception as e:
        logging.error(f"Error durante la solicitud: {str(e)}")
        return False

if __name__ == "__main__":
    resultado = probar_registro_con_log()
    logging.info(f"Resultado final: {'Éxito' if resultado else 'Fallo'}")
    print(f"Prueba completada. Revisa el archivo {log_filename} para más detalles.")
