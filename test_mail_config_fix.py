#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la configuración de correo después del arreglo
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

try:
    from sql_app.Services.mail.mail import MAIL_ENABLED, SMTP_SERVER, USERNAME, PASSWORD
    
    print("🧪 PRUEBA DE CONFIGURACIÓN DE CORREO DESPUÉS DEL ARREGLO")
    print("=" * 60)
    print(f"MAIL_ENABLED: {MAIL_ENABLED}")
    print(f"SMTP_SERVER: {SMTP_SERVER}")
    print(f"USERNAME: {USERNAME}")
    print(f"PASSWORD: {'*' * len(PASSWORD) if PASSWORD else 'None'}")
    
    if MAIL_ENABLED:
        print("\n✅ ¡ÉXITO! La configuración de correo está habilitada")
    else:
        print("\n❌ La configuración de correo sigue deshabilitada")
        
except Exception as e:
    print(f"❌ Error al importar configuración de correo: {e}")
    import traceback
    traceback.print_exc()
