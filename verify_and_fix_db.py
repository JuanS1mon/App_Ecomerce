#!/usr/bin/env python3
"""
Verificar estructura de la base de datos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from sqlalchemy import text, inspect

def check_database_structure():
    """Verifica la estructura de la base de datos"""
    db = SessionLocal()
    
    try:
        print("🔍 VERIFICANDO ESTRUCTURA DE LA BASE DE DATOS")
        print("=" * 60)
        
        # Obtener inspector de la base de datos
        inspector = inspect(engine)
        
        # Listar todas las tablas
        tables = inspector.get_table_names()
        print(f"📊 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table}")
        
        # Verificar tabla de usuarios específicamente
        if 'Usuarios' in tables:
            print(f"\n📋 Estructura de tabla 'Usuarios':")
            columns = inspector.get_columns('Usuarios')
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
        
        # Verificar tabla de roles
        if 'Roles' in tables:
            print(f"\n📋 Estructura de tabla 'Roles':")
            columns = inspector.get_columns('Roles')
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
        
        # Verificar tabla UsuariosRol
        if 'UsuariosRol' in tables:
            print(f"\n📋 Estructura de tabla 'UsuariosRol':")
            columns = inspector.get_columns('UsuariosRol')
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            # Verificar claves foráneas
            fks = inspector.get_foreign_keys('UsuariosRol')
            print(f"🔗 Claves foráneas de UsuariosRol:")
            for fk in fks:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Probar una consulta simple para ver usuarios
        print(f"\n👥 Usuarios en la base de datos:")
        result = db.execute(text("SELECT codigo, usuario, nombre FROM Usuarios"))
        users = result.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, Usuario: {user[1]}, Nombre: {user[2]}")
        
        # Probar consulta para ver roles
        print(f"\n🔑 Roles en la base de datos:")
        try:
            result = db.execute(text("SELECT id, nombre, descripcion FROM Roles"))
            roles = result.fetchall()
            for role in roles:
                print(f"  - ID: {role[0]}, Nombre: {role[1]}, Descripción: {role[2]}")
        except Exception as e:
            print(f"  ❌ Error consultando roles: {e}")
        
        # Probar consulta para ver asignaciones usuario-rol
        print(f"\n🔗 Asignaciones Usuario-Rol:")
        try:
            result = db.execute(text("SELECT usuario_id, rol_id FROM UsuariosRol"))
            assignments = result.fetchall()
            for assignment in assignments:
                print(f"  - Usuario ID: {assignment[0]}, Rol ID: {assignment[1]}")
        except Exception as e:
            print(f"  ❌ Error consultando UsuariosRol: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False
    finally:
        db.close()

def simple_role_assignment():
    """Intenta asignar rol usando SQL directo"""
    db = SessionLocal()
    
    try:
        print(f"\n🔧 ASIGNACIÓN DIRECTA DE ROL CON SQL")
        print("=" * 60)
        
        # Verificar que el usuario testuser existe
        result = db.execute(text("SELECT codigo FROM Usuarios WHERE usuario = 'testuser'"))
        user_row = result.fetchone()
        
        if not user_row:
            print("❌ Usuario 'testuser' no encontrado")
            return False
        
        user_id = user_row[0]
        print(f"✅ Usuario 'testuser' encontrado con ID: {user_id}")
        
        # Verificar que el rol admin existe
        result = db.execute(text("SELECT id FROM Roles WHERE nombre = 'admin'"))
        role_row = result.fetchone()
        
        if not role_row:
            print("⚠️  Rol 'admin' no existe, creándolo...")
            db.execute(text("INSERT INTO Roles (nombre, descripcion) VALUES ('admin', 'Administrador del sistema')"))
            db.commit()
            
            result = db.execute(text("SELECT id FROM Roles WHERE nombre = 'admin'"))
            role_row = result.fetchone()
        
        role_id = role_row[0]
        print(f"✅ Rol 'admin' encontrado con ID: {role_id}")
        
        # Verificar si ya está asignado
        result = db.execute(text("SELECT * FROM UsuariosRol WHERE usuario_id = :user_id AND rol_id = :role_id"), 
                          {"user_id": user_id, "role_id": role_id})
        existing = result.fetchone()
        
        if existing:
            print("✅ El rol ya está asignado")
        else:
            print("📝 Asignando rol...")
            db.execute(text("INSERT INTO UsuariosRol (usuario_id, rol_id) VALUES (:user_id, :role_id)"),
                      {"user_id": user_id, "role_id": role_id})
            db.commit()
            print("✅ Rol asignado exitosamente")
        
        # Verificar la asignación final
        result = db.execute(text("""
            SELECT u.usuario, r.nombre
            FROM Usuarios u
            JOIN UsuariosRol ur ON u.codigo = ur.usuario_id
            JOIN Roles r ON ur.rol_id = r.id
            WHERE u.usuario = 'testuser'
        """))
        
        user_roles = result.fetchall()
        print(f"\n📊 Roles finales del usuario 'testuser':")
        for user_role in user_roles:
            print(f"  - {user_role[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en asignación directa: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO Y REPARACIÓN DE BASE DE DATOS")
    print("=" * 70)
    
    # Verificar estructura
    structure_ok = check_database_structure()
    
    if structure_ok:
        # Intentar asignación directa
        assignment_ok = simple_role_assignment()
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN:")
        print(f"Estructura verificada: {'✅ SÍ' if structure_ok else '❌ NO'}")
        print(f"Asignación exitosa:   {'✅ SÍ' if assignment_ok else '❌ NO'}")
        
        if structure_ok and assignment_ok:
            print("\n🎉 ¡BASE DE DATOS CONFIGURADA CORRECTAMENTE!")
        else:
            print("\n⚠️  Revisar errores en la configuración.")
    else:
        print("\n❌ No se pudo verificar la estructura de la base de datos.")
