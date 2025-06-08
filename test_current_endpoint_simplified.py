#!/usr/bin/env python3
"""
Script simplificado para probar el endpoint /usuarios/current
"""

import sys
import os
sys.path.append('c:/Users/PCJuan/Desktop/sql_app/sql_app')

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Import desde los módulos específicos
try:
    from sql_app.db.database import SessionLocal
    from sql_app.main import app
except ImportError:
    # Si no funciona, intentar import directo
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql_app'))
    from db.database import SessionLocal
    from main import app

# Crear cliente de prueba
client = TestClient(app)

def test_without_token():
    """Probar sin token"""
    print("============================================================")
    print("🔍 PROBAR ENDPOINT SIN TOKEN")
    print("============================================================")
    
    response = client.get("/usuarios/current")
    print(f"Status Code: {response.status_code}")
    print(f"Response Type: {type(response.content)}")
    
    if response.status_code == 307:
        print(f"✅ Redirección correcta a: {response.headers.get('location', 'Sin ubicación')}")
    else:
        print(f"Response content: {response.content[:200]}...")

def test_with_dummy_token():
    """Probar con token dummy"""
    print("\n============================================================")
    print("🔍 PROBAR ENDPOINT CON TOKEN DUMMY")
    print("============================================================")
    
    headers = {"Authorization": "Bearer token_invalido"}
    response = client.get("/usuarios/current", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Respuesta exitosa: {response.json()}")
    elif response.status_code == 307:
        print(f"🔄 Redirección a: {response.headers.get('location', 'Sin ubicación')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response content: {response.content[:200]}...")

def check_users_in_db():
    """Verificar si hay usuarios en la base de datos"""
    print("\n============================================================")
    print("🔍 VERIFICAR USUARIOS EN BD")
    print("============================================================")
    
    try:
        db = SessionLocal()
        from db.models.config.usuarios import usuarios as UsuariosModel
        
        users = db.query(UsuariosModel).limit(5).all()
        print(f"Usuarios encontrados: {len(users)}")
        
        for user in users:
            print(f"- Usuario: {user.usuario} (ID: {user.codigo}) - Activo: {user.activo}")
            
        db.close()
        return len(users) > 0
        
    except Exception as e:
        print(f"❌ Error consultando BD: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PRUEBA SIMPLIFICADA DEL ENDPOINT /usuarios/current")
    print("=" * 60)
    
    # Verificar usuarios en BD
    has_users = check_users_in_db()
    
    # Probar endpoint
    test_without_token()
    test_with_dummy_token()
    
    print("\n============================================================")
    print("✅ PRUEBAS COMPLETADAS")
    print("============================================================")
