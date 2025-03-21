import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import re
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

# Modelo de solicitud
class EmailRequest(BaseModel):
    destinatario: str
    asunto: str
    mensaje: str

# Cargar variables de entorno desde .env
load_dotenv()

# Configuracion de correo



SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))  # Convertir a int ya que los puertos son números
USERNAME = os.getenv('USERNAMEmail')  # Asegúrate de que 'USERNAME_EMAIL' está correctamente definido en .env
PASSWORD = os.getenv('PASSWORDmail')

# Crear el router de FastAPI
router = APIRouter(
    include_in_schema=False ,  # Oculta todas las rutas de este router en la documentación
    prefix="/envios",
    tags=["envios"],
    responses={404: {"description": "Not Found"}},
)

# Ruta de FastAPI para enviar correo
# Ruta de FastAPI para enviar correo
@router.post("/enviar_correo")
async def enviar_correo_route(request: EmailRequest):
    # Validar el email
    destinatario = validar_email(request.destinatario)
    if not destinatario:
        raise HTTPException(status_code=400, detail="Correo electrónico inválido")
    # Enviar el correo
    try:
        enviar_correo(destinatario, request.asunto, request.mensaje)
        return {'mensaje': "Correo enviado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")
    
def enviar_correo(destinatario, asunto, mensaje):
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
    except Exception as e:

        raise e  # Propagar la excepción

def validar_email(email):
    # Expresión regular para validar el formato del correo electrónico
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(patron, email):
        return email
    else:
        return None