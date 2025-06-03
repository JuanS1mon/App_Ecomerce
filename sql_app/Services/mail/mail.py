import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import os.path
from dotenv import load_dotenv
import os
import re
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

# Modelo de solicitud
class EmailRequest(BaseModel):
    destinatario: str
    asunto: str
    mensaje: str

class EmailConAdjuntoRequest(BaseModel):
    destinatario: str
    asunto: str
    mensaje: str
    rutas_archivos: List[str] = []

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

def enviar_email_con_adjunto(destinatario, asunto, mensaje, rutas_archivos):
    """
    Envía un correo electrónico con archivos adjuntos.
    
    Args:
        destinatario: Dirección de correo del destinatario
        asunto: Asunto del correo
        mensaje: Cuerpo del mensaje
        rutas_archivos: Lista de rutas a los archivos que se adjuntarán
    
    Returns:
        None
    
    Raises:
        Exception: Si ocurre algún error durante el envío
    """
    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = asunto
    
    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(mensaje, 'plain'))
    
    # Adjuntar cada archivo
    for ruta_archivo in rutas_archivos:
        if os.path.isfile(ruta_archivo):
            # Obtener el nombre del archivo de la ruta
            nombre_archivo = os.path.basename(ruta_archivo)
            
            # Detectar el tipo de archivo y adjuntarlo de manera apropiada
            with open(ruta_archivo, "rb") as archivo:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(archivo.read())
            
            # Codificar para enviar por correo
            encoders.encode_base64(part)
            
            # Agregar cabecera con el nombre del archivo
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{nombre_archivo}"'
            )
            
            # Agregar el archivo adjunto al mensaje
            msg.attach(part)
    
    # Enviar el correo
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        text = msg.as_string()
        server.sendmail(USERNAME, destinatario, text)
        server.quit()
    except Exception as e:
        raise e  # Propagar la excepción

@router.post("/enviar_email_con_adjunto")
async def enviar_email_con_adjunto_route(request: EmailConAdjuntoRequest):
    """
    Ruta para enviar un correo electrónico con archivos adjuntos
    """
    # Validar el email
    destinatario = validar_email(request.destinatario)
    if not destinatario:
        raise HTTPException(status_code=400, detail="Correo electrónico inválido")
    
    # Validar que los archivos existan
    archivos_no_encontrados = []
    for ruta in request.rutas_archivos:
        if not os.path.isfile(ruta):
            archivos_no_encontrados.append(ruta)
    
    if archivos_no_encontrados:
        raise HTTPException(
            status_code=400, 
            detail=f"Los siguientes archivos no fueron encontrados: {', '.join(archivos_no_encontrados)}"
        )
    
    # Enviar el correo con los adjuntos
    try:
        enviar_email_con_adjunto(
            destinatario, 
            request.asunto, 
            request.mensaje, 
            request.rutas_archivos
        )
        return {'mensaje': "Correo con archivos adjuntos enviado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al enviar el correo con adjuntos: {str(e)}"
        )

@router.post("/enviar_email_con_adjunto_upload")
async def enviar_email_con_adjunto_upload(
    destinatario: str = Form(...),
    asunto: str = Form(...),
    mensaje: str = Form(...),
    archivos: List[UploadFile] = File(...)
):
    """
    Ruta para enviar un correo electrónico con archivos adjuntos subidos directamente
    """
    # Validar el email
    destinatario_valido = validar_email(destinatario)
    if not destinatario_valido:
        raise HTTPException(status_code=400, detail="Correo electrónico inválido")
    
    # Directorio temporal para guardar los archivos subidos
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Lista para almacenar las rutas temporales de los archivos
    rutas_temporales = []
    
    try:
        # Guardar cada archivo en el directorio temporal
        for archivo in archivos:
            # Generar un nombre de archivo único para evitar colisiones
            nombre_temporal = f"{temp_dir}/{archivo.filename}"
            
            # Guardar el archivo
            with open(nombre_temporal, "wb") as buffer:
                content = await archivo.read()
                buffer.write(content)
            
            # Añadir la ruta a la lista
            rutas_temporales.append(nombre_temporal)
        
        # Enviar el correo con los archivos adjuntos
        enviar_email_con_adjunto(
            destinatario_valido, 
            asunto, 
            mensaje, 
            rutas_temporales
        )
        
        # Eliminar los archivos temporales después de enviar el correo
        for ruta in rutas_temporales:
            if os.path.exists(ruta):
                os.remove(ruta)
        
        return {'mensaje': "Correo con archivos adjuntos enviado exitosamente"}
    
    except Exception as e:
        # Asegurarse de limpiar los archivos temporales en caso de error
        for ruta in rutas_temporales:
            if os.path.exists(ruta):
                os.remove(ruta)
                
        raise HTTPException(
            status_code=500, 
            detail=f"Error al enviar el correo con adjuntos: {str(e)}"
        )