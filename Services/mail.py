import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import re
# Cargar variables de entorno desde .env
load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))  # Convertir a int ya que los puertos son números
USERNAME = os.getenv('USERNAMEmail')
PASSWORD = os.getenv('PASSWORDmail')


# Función para enviar correo
def enviar_correo(destinatario, asunto, mensaje):
	print(SMTP_SERVER) 
	print(SMTP_PORT) 
	msg = MIMEMultipart()
	msg['From'] = USERNAME
	msg['To'] = destinatario
	msg['Subject'] = asunto
	msg.attach(MIMEText(mensaje, 'plain'))
	try:
		server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
		server.starttls()
		server.login(USERNAME, PASSWORD)
		text = msg.as_string()
		server.sendmail(USERNAME, destinatario, text)
		server.quit()
		print("Correo enviado exitosamente a", destinatario)
	except Exception as e:
		print("Error al enviar el correo:", e)



def validar_email(email):
    # Expresión regular para validar el formato del correo electrónico
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    if re.match(patron, email):
        return email
    else:
        return None