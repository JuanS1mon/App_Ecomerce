#!/usr/bin/env python3
"""
Script para asignar rol de administrador al usuario testuser
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models.config.usuarios import usuarios
from db.models.config.roles import roles as RolesModel
from db.models.config.usuarios_rol import usuarios_rol as UsuariosRolModel
from sqlalchemy import text

def assign_admin_role():
    """Asigna rol de administrador al usuario testuser"""
    db = SessionLocal()
    
    try:
        print("🔍 ASIGNANDO ROL DE ADMINISTRADOR A TESTUSER")
        print("=" * 50)
        
        # 1. Verificar que el usuario testuser existe
        user = db.query(usuarios).filter(usuarios.usuario == "testuser").first()
        if not user:
            print("❌ Usuario 'testuser' no encontrado")
            return False
        
        print(f"✅ Usuario encontrado: {user.usuario} (ID: {user.codigo})")        # 2. Verificar/crear rol admin
        admin_role = db.query(RolesModel).filter(RolesModel.nombre == "admin").first()
        if not admin_role:
            print("⚠️  Rol 'admin' no existe, creándolo...")
            admin_role = RolesModel(
                nombre="admin",
                descripcion="Administrador del sistema"
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"✅ Rol 'admin' creado (ID: {admin_role.id})")
        else:
            print(f"✅ Rol 'admin' existe (ID: {admin_role.id})")
        
        # 3. Verificar si ya tiene el rol asignado
        existing_assignment = db.query(UsuariosRolModel).filter(
            UsuariosRolModel.usuario_id == user.codigo,
            UsuariosRolModel.rol_id == admin_role.id
        ).first()
        
        if existing_assignment:
            print("✅ Usuario ya tiene rol de administrador asignado")
        else:
            print("📝 Asignando rol de administrador...")
            user_role = UsuariosRolModel(
                usuario_id=user.codigo,
                rol_id=admin_role.id
            )
            db.add(user_role)
            db.commit()
            print("✅ Rol de administrador asignado exitosamente")
        
        # 4. Verificar la asignación
        result = db.execute(text("""
            SELECT u.usuario, r.nombre
            FROM Usuarios u
            JOIN UsuariosRol ur ON u.codigo = ur.usuario_id
            JOIN Roles r ON ur.rol_id = r.id
            WHERE u.usuario = 'testuser'
        """))
        
        roles = result.fetchall()
        print(f"\n📊 Roles actuales del usuario 'testuser':")
        for role in roles:
            print(f"  - {role[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error asignando rol: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_admin_access():
    """Verifica el acceso de admin después de asignar rol"""
    import requests
    
    print("\n🔍 VERIFICANDO ACCESO DE ADMIN")
    print("=" * 50)
    
    # Login
    login_data = {
        "username": "testuser", 
        "password": "Test123456"
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        # Obtener token
        response = requests.post("http://localhost:8000/login", data=login_data, headers=headers)
        if response.status_code != 200:
            print(f"❌ Login falló: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        print(f"✅ Token obtenido: {token[:50]}...")
        
        # Probar acceso a /admin con Authorization header
        auth_headers = {"Authorization": f"Bearer {token}"}
        admin_response = requests.get("http://localhost:8000/admin", headers=auth_headers)
        
        print(f"📍 Acceso a /admin: Status {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("✅ ¡Acceso de administrador exitoso!")
            return True
        else:
            print(f"❌ Acceso denegado: {admin_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando acceso: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CONFIGURANDO ACCESO DE ADMINISTRADOR PARA TESTUSER")
    print("=" * 60)
    
    # Paso 1: Asignar rol
    role_assigned = assign_admin_role()
    
    if role_assigned:
        # Paso 2: Verificar acceso
        access_granted = verify_admin_access()
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN:")
        print(f"Rol asignado:     {'✅ SÍ' if role_assigned else '❌ NO'}")
        print(f"Acceso verificado: {'✅ SÍ' if access_granted else '❌ NO'}")
        
        if role_assigned and access_granted:
            print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            print("   El usuario 'testuser' ahora tiene acceso de administrador")
        else:
            print("\n⚠️  Configuración parcial. Revisar logs para más detalles.")
    else:
        print("\n❌ No se pudo asignar el rol. Revisar errores.")
