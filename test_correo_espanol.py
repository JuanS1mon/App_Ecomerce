# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el servicio de correo funciona con caracteres especiales en español
"""

import asyncio
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sql_app.Services.mail.mail import enviar_email_simple
    print("✅ Importación exitosa del servicio de correo")
except Exception as e:
    print(f"❌ Error al importar el servicio de correo: {e}")
    exit(1)

def test_correo_con_caracteres_especiales():
    """
    Prueba el envío de correo con caracteres especiales (ñ, acentos, etc.)
    """
    print("\n🧪 Probando envío de correo con caracteres especiales...")
    
    # Mensaje con caracteres especiales
    destinatario = "test@ejemplo.com"  # Cambia por un email real para probar
    asunto = "Prueba de contraseña y configuración"
    mensaje = """
    Hola,
    
    Este es un mensaje de prueba para verificar que el sistema de correo
    puede manejar correctamente caracteres especiales del español:
    
    - Eñes: año, niño, diseño, señor
    - Acentos: configuración, contraseña, validación, información
    - Signos: ¿Cómo estás? ¡Excelente!
    
    Si recibes este correo sin problemas, el sistema está funcionando correctamente.
    
    Saludos,
    Sistema de SQL App
    """
    
    try:
        resultado = enviar_email_simple(destinatario, asunto, mensaje)
        print(f"✅ Resultado: {resultado}")
        return True
    except ValueError as e:
        print(f"⚠️  Error de validación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False

def test_validacion_variables_entorno():
    """
    Verifica que las variables de entorno estén configuradas
    """
    print("\n🔍 Verificando configuración de variables de entorno...")
    
    from sql_app.Services.mail.mail import SMTP_SERVER, USERNAME, PASSWORD, MAIL_FROM
    
    variables = {
        'SMTP_SERVER': SMTP_SERVER,
        'USERNAME': USERNAME,
        'PASSWORD': PASSWORD,
        'MAIL_FROM': MAIL_FROM
    }
    
    for nombre, valor in variables.items():
        if valor and valor != f"tu_{nombre.lower()}":
            print(f"✅ {nombre}: Configurado")
        else:
            print(f"❌ {nombre}: NO configurado o usa valor de ejemplo")
    
    return all(valor and not valor.startswith('tu_') for valor in variables.values())

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del servicio de correo...")
    
    # Verificar configuración
    config_ok = test_validacion_variables_entorno()
    
    if config_ok:
        print("\n✅ Configuración correcta. Procediendo con la prueba de envío...")
        # Solo ejecutar si quieres enviar un correo real
        print("\n⚠️  Para enviar un correo real, cambia 'test@ejemplo.com' por tu email en el código")
        print("   y descomenta la siguiente línea:")
        # test_correo_con_caracteres_especiales()
    else:
        print("\n❌ Configuración incompleta. Verifica tu archivo .env:")
        print("   - USERNAME_EMAIL: tu email de Gmail")
        print("   - PASSWORD_EMAIL: tu contraseña de aplicación de Gmail")
        print("   - MAIL_FROM: mismo email que USERNAME_EMAIL")
    
    print("\n✅ Pruebas completadas.")
