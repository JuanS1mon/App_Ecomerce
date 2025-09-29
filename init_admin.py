#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos con el usuario administrador 'juan'
"""

import sqlite3
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sql_app.Services.security.security import encriptar_clave

def init_admin_user():
    """Inicializa la base de datos con el usuario admin 'juan'"""
    
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    print("=== INICIALIZANDO BASE DE DATOS CON USUARIO ADMIN ===")
    
    try:
        # 1. Crear rol de administrador si no existe
        print("1. Creando rol de administrador...")
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'admin'")
        admin_role = cursor.fetchone()
        
        if not admin_role:
            cursor.execute("""
                INSERT INTO Roles (nombre, descripcion) 
                VALUES ('admin', 'Administrador del sistema con acceso completo')
            """)
            admin_role_id = cursor.lastrowid
            print(f"   ✅ Rol 'admin' creado con ID: {admin_role_id}")
        else:
            admin_role_id = admin_role[0]
            print(f"   ℹ️  Rol 'admin' ya existe con ID: {admin_role_id}")
        
        # 2. Crear usuario 'juan' si no existe
        print("2. Creando usuario 'juan'...")
        cursor.execute("SELECT codigo FROM Usuarios WHERE usuario = 'juan'")
        juan_user = cursor.fetchone()
        
        if not juan_user:
            # Encriptar contraseña
            password_plain = "admin123"  # Contraseña por defecto
            password_hash = encriptar_clave(password_plain)
            
            cursor.execute("""
                INSERT INTO Usuarios (usuario, nombre, mail, activo, clave, fecha_creacion) 
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, ("juan", "Juan Administrador", "juan@admin.com", True, password_hash))
            
            juan_user_id = cursor.lastrowid
            print(f"   ✅ Usuario 'juan' creado con ID: {juan_user_id}")
            print(f"   🔑 Contraseña inicial: {password_plain}")
            
        else:
            juan_user_id = juan_user[0]
            print(f"   ℹ️  Usuario 'juan' ya existe con ID: {juan_user_id}")
        
        # 3. Asignar rol de admin al usuario juan
        print("3. Asignando rol de administrador a 'juan'...")
        cursor.execute("""
            SELECT usuario_id FROM usuario_roles 
            WHERE usuario_id = ? AND rol_id = ?
        """, (juan_user_id, admin_role_id))
        
        existing_relation = cursor.fetchone()
        
        if not existing_relation:
            cursor.execute("""
                INSERT INTO usuario_roles (usuario_id, rol_id) 
                VALUES (?, ?)
            """, (juan_user_id, admin_role_id))
            print(f"   ✅ Rol 'admin' asignado al usuario 'juan'")
        else:
            print(f"   ℹ️  Usuario 'juan' ya tiene el rol 'admin'")
        
        # 4. Crear otros roles básicos
        print("4. Creando roles básicos adicionales...")
        roles_basicos = [
            ("usuario", "Usuario estándar con permisos básicos"),
            ("manager", "Gestor con permisos avanzados"),
            ("tecnico", "Técnico de soporte")
        ]
        
        for nombre_rol, descripcion_rol in roles_basicos:
            cursor.execute("SELECT id FROM Roles WHERE nombre = ?", (nombre_rol,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Roles (nombre, descripcion) 
                    VALUES (?, ?)
                """, (nombre_rol, descripcion_rol))
                print(f"   ✅ Rol '{nombre_rol}' creado")
            else:
                print(f"   ℹ️  Rol '{nombre_rol}' ya existe")
        
        # Confirmar cambios
        conn.commit()
        
        print("\n=== VERIFICACIÓN FINAL ===")
        
        # Verificar usuario
        cursor.execute("""
            SELECT u.codigo, u.usuario, u.nombre, u.mail, u.activo
            FROM Usuarios u 
            WHERE u.usuario = 'juan'
        """)
        user_info = cursor.fetchone()
        if user_info:
            print(f"✅ Usuario 'juan' confirmado:")
            print(f"   ID: {user_info[0]}")
            print(f"   Usuario: {user_info[1]}")
            print(f"   Nombre: {user_info[2]}")
            print(f"   Email: {user_info[3]}")
            print(f"   Activo: {user_info[4]}")
        
        # Verificar roles
        cursor.execute("""
            SELECT r.nombre 
            FROM Roles r
            JOIN usuario_roles ur ON r.id = ur.rol_id
            JOIN Usuarios u ON ur.usuario_id = u.codigo
            WHERE u.usuario = 'juan'
        """)
        roles = cursor.fetchall()
        if roles:
            print(f"✅ Roles asignados a 'juan': {[role[0] for role in roles]}")
        
        print("\n🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!")
        print(f"🔐 Puedes iniciar sesión con:")
        print(f"   Usuario: juan")
        print(f"   Contraseña: admin123")
        print(f"   URL: http://127.0.0.1:8000/loginpage")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_admin_user()