#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para revisar la configuración de correo
"""

import os
from dotenv import load_dotenv

def debug_mail_config():
    print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN DE CORREO")
    print("=" * 50)
    
    # 1. Verificar si el archivo .env existe
    env_paths = [
        "sql_app/.env",
        ".env",
        "sql_app/sql_app/.env"
    ]
    
    env_file_found = None
    for path in env_paths:
        if os.path.exists(path):
            env_file_found = path
            print(f"✅ Archivo .env encontrado en: {path}")
            break
    
    if not env_file_found:
        print("❌ No se encontró archivo .env en las rutas:")
        for path in env_paths:
            print(f"   - {path}")
        return
    
    # 2. Cargar variables de entorno
    print(f"\n📂 Cargando variables desde: {env_file_found}")
    load_dotenv(env_file_found)
    
    # 3. Verificar variables de correo específicas
    mail_vars = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_USE_TLS': os.getenv('SMTP_USE_TLS'),
        'SMTP_USE_SSL': os.getenv('SMTP_USE_SSL'),
        'USERNAME_EMAIL': os.getenv('USERNAME_EMAIL'),
        'PASSWORD_EMAIL': os.getenv('PASSWORD_EMAIL'),
        'MAIL_FROM': os.getenv('MAIL_FROM'),
        'MAIL_FROM_NAME': os.getenv('MAIL_FROM_NAME'),
    }
    
    print("\n📧 VARIABLES DE CORREO:")
    print("-" * 30)
    
    for var_name, var_value in mail_vars.items():
        if var_value:
            # Ocultar contraseñas para seguridad
            if 'PASSWORD' in var_name:
                display_value = "*" * len(var_value) if var_value else "None"
            else:
                display_value = var_value
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: No configurada")
    
    # 4. Verificar las variables críticas
    critical_vars = [mail_vars['SMTP_SERVER'], mail_vars['USERNAME_EMAIL'], mail_vars['PASSWORD_EMAIL']]
    
    print(f"\n🎯 VALIDACIÓN CRÍTICA:")
    print("-" * 25)
    
    if all(critical_vars):
        print("✅ Todas las variables críticas están configuradas")
        print("✅ El correo debería estar funcionando")
    else:
        print("❌ Variables críticas faltantes:")
        if not mail_vars['SMTP_SERVER']:
            print("   - SMTP_SERVER")
        if not mail_vars['USERNAME_EMAIL']:
            print("   - USERNAME_EMAIL")
        if not mail_vars['PASSWORD_EMAIL']:
            print("   - PASSWORD_EMAIL")
    
    # 5. Revisar contenido del archivo .env (primeras líneas)
    print(f"\n📄 CONTENIDO DEL ARCHIVO .env (primeras 10 líneas):")
    print("-" * 45)
    try:
        with open(env_file_found, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines, 1):
                # No mostrar líneas con contraseñas completas
                if 'PASSWORD' in line:
                    line = line.split('=')[0] + '=***hidden***\n'
                print(f"{i:2}: {line.rstrip()}")
    except Exception as e:
        print(f"Error leyendo archivo: {e}")

if __name__ == "__main__":
    debug_mail_config()
