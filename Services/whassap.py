import pywhatkit as kit
import pyautogui
import time
import re


def enviar_mensaje_whatsapp(numero, mensaje):
    # Envía un mensaje de WhatsApp a un número específico de inmediato usando la aplicación de WhatsApp
    kit.sendwhatmsg_instantly(numero, mensaje, 10, True, 2)
    time.sleep(10)  # Espera a que se abra WhatsApp y se escriba el mensaje
    pyautogui.press('enter')  # Simula la pulsación de la tecla Enter

def validar_telefono(telefono: str) -> bool:
    # Expresión regular para validar el formato del número de teléfono
    patron = re.compile(r'^\+\d{11}$')
    return bool(patron.match(telefono))

def ajustar_telefono(telefono: str) -> str:
    # Ajusta el número de teléfono al formato +54 9 seguido del número
    if telefono.startswith('15'):
        telefono = telefono[2:]  # Elimina el prefijo '15'
    return f'+54 9{telefono}'


