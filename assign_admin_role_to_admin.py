#!/usr/bin/env python3
"""
Script para asignar rol de administrador al usuario admin
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

def assign_admin_role_to_admin():
    """Asigna rol de administrador al usuario admin"""
    db = SessionLocal()
    
    try:
        print("🔍 ASIGNANDO ROL DE ADMINISTRADOR AL USUARIO ADMIN")
        print("=" * 55)
        
        # 1. Verificar que el usuario admin existe
        user = db.query(usuarios).filter(usuarios.usuario == "admin").first()
        if not user:
            print("❌ Usuario 'admin' no encontrado")
            return False
        
        print(f"✅ Usuario encontrado: {user.usuario} (ID: {user.codigo})")
        
        # 2. Verificar/crear rol admin
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
            JOIN usuarios_rol ur ON u.codigo = ur.usuario_id
            JOIN roles r ON ur.rol_id = r.id
            WHERE u.usuario = 'admin'
        """)).fetchall()
        
        print("\n📋 ROLES DEL USUARIO ADMIN:")
        for row in result:
            print(f"   • Usuario: {row[0]} | Rol: {row[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_admin_access():
    """Verifica el acceso de admin después de asignar rol"""
    print("\n🔒 VERIFICANDO ACCESO DE ADMINISTRADOR")
    print("=" * 40)
    
    import requests
    
    try:
        # 1. Login
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = requests.post(
            "http://localhost:8001/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        token = token_data.get('access_token')
        
        print("✅ Login exitoso")
        
        # 2. Verificar roles en el token
        user_info = token_data.get('user_info', {})
        roles = user_info.get('roles', [])
        print(f"🎭 Roles en token: {roles}")
        
        # 3. Probar acceso a /admin
        admin_response = requests.get(
            "http://localhost:8001/admin",
            headers={'Authorization': f'Bearer {token}'},
            allow_redirects=False
        )
        
        print(f"🏢 Status de /admin: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("✅ ¡ACCESO A ADMIN EXITOSO!")
            return True
        elif admin_response.status_code in [307, 302, 301]:
            redirect = admin_response.headers.get('location', 'No location')
            print(f"🔄 Redirect a: {redirect}")
            return False
        else:
            print(f"❌ Error de acceso: {admin_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando acceso: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CONFIGURANDO ACCESO DE ADMINISTRADOR PARA USUARIO ADMIN")
    print("=" * 65)
    
    # Paso 1: Asignar rol
    role_assigned = assign_admin_role_to_admin()
    
    if role_assigned:
        # Paso 2: Verificar acceso
        access_granted = verify_admin_access()
        
        if access_granted:
            print("\n🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
            print("✅ El usuario 'admin' ahora puede acceder al panel de administración")
        else:
            print("\n⚠️  ROL ASIGNADO PERO ACCESO FALLÓ")
            print("🔧 Puede necesitar reiniciar el servidor o verificar la lógica de roles")
    else:
        print("\n❌ NO SE PUDO COMPLETAR LA CONFIGURACIÓN")
        print("🔧 Revisar errores en la asignación de roles")
