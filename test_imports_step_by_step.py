#!/usr/bin/env python3
"""
Script para identificar exactamente qué importación está causando el problema
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_imports_step_by_step():
    print("🔍 TESTANDO IMPORTACIONES PASO A PASO")
    print("=" * 50)
    
    try:
        print("1. FastAPI imports...")
        from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks, Request
        from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, FileResponse
        from fastapi.security import OAuth2PasswordRequestForm
        from fastapi.templating import Jinja2Templates
        print("   ✅ FastAPI imports OK")
        
        print("2. Standard libraries...")
        import httpx
        from pydantic import BaseModel, EmailStr, field_validator, Field
        from sqlalchemy.orm import Session
        import os
        from dotenv import load_dotenv
        from datetime import timedelta, datetime
        import logging
        import secrets
        import re
        import jwt
        from typing import Optional
        print("   ✅ Standard libraries OK")
        
        print("3. Security imports...")
        from sql_app.Services.security.security_improved import (ACCESS_TOKEN_DURATION, authenticate_user, current_user, encriptar_clave, verificar_clave, crear_access_token,decodifica_token,validate_username,validate_password_strength,log_security_event,revoke_token,generar_token_activacion, SECRET, ALGORITHM)
        print("   ✅ Security imports OK")
        
        print("4. Other services...")
        from sql_app.Services.security.get_optional_user import get_optional_user
        from sql_app.Services.mail.mail import enviar_email_simple, validar_email
        from sql_app.Services.comunicacion.whassap import enviar_mensaje_whatsapp, validar_telefono
        print("   ✅ Other services OK")
        
        print("5. Database imports...")
        from sql_app.db.crud.config.Usuarios import (
            get_usuario, 
            create_usuario, 
            update_usuario_activate
        )
        from sql_app.db.database import get_db
        from sql_app.db.schemas.config.Usuarios import (
            UserDB, 
            PasswordReset, 
            PasswordResetRequest
        )
        from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
        print("   ✅ Database imports OK")
        
        print("\n🎉 TODAS LAS IMPORTACIONES EXITOSAS")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en este paso: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports_step_by_step()
