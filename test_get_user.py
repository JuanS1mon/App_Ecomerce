#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar directamente la función get_user_from_token
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from sql_app.db.database import engine
from sql_app.Services.security.auth_middleware import get_user_from_token

def test_get_user_from_token():
    """Prueba la función get_user_from_token directamente"""
    
    print("=== PRUEBA DE GET_USER_FROM_TOKEN ===")
    
    try:
        # Crear sesión de base de datos
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Token de prueba (el mismo del error)
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdWFuIiwiZXhwIjoxNzU5MTA3Mjc3fQ.ui5QGsBDMhuMIPg6SUvel2LoPAi8nfQcwYC-QtlmrXY"
        
        print(f"Token a probar: {token[:50]}...")
        
        # Llamar a la función
        user = get_user_from_token(token, db)
        
        print(f"✅ Usuario obtenido exitosamente:")
        print(f"   Código: {user.codigo}")
        print(f"   Usuario: {user.usuario}")
        print(f"   Nombre: {user.nombre}")
        print(f"   Email: {user.mail}")
        print(f"   Activo: {user.activo}")
        print(f"   Roles: {user.roles}")
        
        # Verificar específicamente si es admin
        is_admin = "admin" in user.roles
        print(f"   ¿Es admin?: {is_admin}")
        
    except Exception as e:
        print(f"❌ Error en get_user_from_token: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_get_user_from_token()