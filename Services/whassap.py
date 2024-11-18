import pywhatkit as kit
import pyautogui
import time
import re
import logging
from fastapi import HTTPException
from pywhatkit.core.exceptions import CountryCodeException

def enviar_mensaje_whatsapp(numero, mensaje):
    try:
        # Envía un mensaje de WhatsApp a un número específico de inmediato usando la aplicación de WhatsApp
        kit.sendwhatmsg_instantly(numero, mensaje, 10, True, 2)
        time.sleep(30)  # Espera a que se abra WhatsApp y se escriba el mensaje
        pyautogui.press('enter')  # Simula la pulsación de la tecla Enter
    except CountryCodeException:
        logging.warning("No se pudo enviar el mensaje de WhatsApp. Código de país faltante en el número de teléfono.")
        raise HTTPException(status_code=200, detail="No se pudo enviar el mensaje de WhatsApp. Por favor, revise su correo electrónico para activar su cuenta.")
    except Exception as e:
        logging.error(f"Error al enviar el mensaje de WhatsApp: {str(e)}")
        raise HTTPException(status_code=200, detail="No se pudo enviar el mensaje de WhatsApp. Por favor, revise su correo electrónico para activar su cuenta.")

def validar_telefono(telefono: str) -> bool:
    # Expresión regular para validar el formato del número de teléfono
    patron = re.compile(r'^\+\d{11,15}$')
    return bool(patron.match(telefono))

def enviar_correo_activacion(destino, mensaje):
    # Función de ejemplo para enviar correos electrónicos
    # Aquí puedes implementar el envío de correos electrónicos utilizando una biblioteca como smtplib
    logging.info(f"Enviando correo de activación a {destino} con el mensaje: {mensaje}")