#!/usr/bin/env python3
"""
Script de debug para verificar credenciales de login
"""
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from sql_app.db.database import get_db
from sql_app.db.models.config.usuarios import Usuarios
from sql_app.Services.security.security import verificar_clave, encriptar_clave

def debug_user_credentials(username: str, test_password: str):
    """Debug de credenciales de usuario"""
    print(f"🔍 DEBUGGING CREDENCIALES PARA: {username}")
    print(f"🔍 CONTRASEÑA A PROBAR: {test_password}")
    print("=" * 50)
    
    # Obtener sesión de base de datos
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Buscar usuario
        user = db.query(Usuarios).filter(Usuarios.usuario == username).first()
        
        if not user:
            print(f"❌ Usuario '{username}' NO encontrado en la base de datos")
            return False
            
        print(f"✅ Usuario encontrado: {user.usuario}")
        print(f"   - Código: {user.codigo}")
        print(f"   - Nombre: {user.nombre}")
        print(f"   - Email: {user.mail}")
        print(f"   - Activo: {user.activo}")
        print(f"   - Hash actual: {user.clave[:30]}...")
        print(f"   - Longitud hash: {len(user.clave) if user.clave else 0}")
        
        if not user.activo:
            print(f"❌ Usuario '{username}' está INACTIVO")
            return False
            
        # Verificar contraseña
        print(f"\n🔑 Verificando contraseña '{test_password}'...")
        is_valid = verificar_clave(test_password, user.clave)
        
        if is_valid:
            print(f"✅ ¡CONTRASEÑA CORRECTA!")
            return True
        else:
            print(f"❌ Contraseña incorrecta")
            
            # Generar hash de la contraseña para comparar
            print(f"\n🔧 Hash que debería tener:")
            new_hash = encriptar_clave(test_password)
            print(f"   Nuevo hash: {new_hash[:30]}...")
            print(f"   ¿Coinciden?: {new_hash == user.clave}")
            
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # Test con las credenciales actuales
    username = "juan"
    password = "qwe123"
    
    print("🚀 INICIANDO DEBUG DE LOGIN")
    debug_user_credentials(username, password)
