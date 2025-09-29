#!/usr/bin/env python3
"""Script para verificar la estructura de las tablas de roles"""

import sqlite3
import sys
import os

def verify_database():
    """Verificar la estructura de la base de datos"""
    db_path = "sql_app.db"
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 === VERIFICACIÓN DE BASE DE DATOS ===")
        
        # Listar todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tablas encontradas: {[table[0] for table in tables]}")
        
        # Verificar tabla Roles
        try:
            cursor.execute("PRAGMA table_info(Roles)")
            roles_schema = cursor.fetchall()
            print(f"\n🏷️ Esquema tabla Roles:")
            for col in roles_schema:
                print(f"  - {col[1]} ({col[2]})")
                
            # Contar roles
            cursor.execute("SELECT COUNT(*) FROM Roles")
            roles_count = cursor.fetchone()[0]
            print(f"  📊 Total roles: {roles_count}")
            
            # Mostrar roles existentes
            cursor.execute("SELECT id, nombre, descripcion FROM Roles")
            roles = cursor.fetchall()
            for rol in roles:
                print(f"    - ID: {rol[0]}, Nombre: {rol[1]}, Descripción: {rol[2]}")
                
        except sqlite3.OperationalError as e:
            print(f"⚠️ Tabla Roles no existe o tiene problemas: {e}")
        
        # Verificar tabla usuario_roles
        try:
            cursor.execute("PRAGMA table_info(usuario_roles)")
            usuario_roles_schema = cursor.fetchall()
            print(f"\n🔗 Esquema tabla usuario_roles:")
            for col in usuario_roles_schema:
                print(f"  - {col[1]} ({col[2]})")
                
            # Contar relaciones
            cursor.execute("SELECT COUNT(*) FROM usuario_roles")
            relations_count = cursor.fetchone()[0]
            print(f"  📊 Total relaciones usuario-rol: {relations_count}")
            
            # Mostrar relaciones existentes
            cursor.execute("""
                SELECT ur.usuario_id, ur.rol_id, u.usuario, r.nombre 
                FROM usuario_roles ur
                LEFT JOIN Usuarios u ON ur.usuario_id = u.codigo
                LEFT JOIN Roles r ON ur.rol_id = r.id
            """)
            relations = cursor.fetchall()
            for rel in relations:
                print(f"    - Usuario ID: {rel[0]} ({rel[2]}) -> Rol ID: {rel[1]} ({rel[3]})")
                
        except sqlite3.OperationalError as e:
            print(f"⚠️ Tabla usuario_roles no existe o tiene problemas: {e}")
        
        # Verificar usuarios y sus roles en la columna 'rol'
        try:
            cursor.execute("SELECT codigo, usuario, rol FROM Usuarios WHERE rol IS NOT NULL")
            usuarios_con_rol = cursor.fetchall()
            print(f"\n👥 Usuarios con rol en columna 'rol':")
            for user in usuarios_con_rol:
                print(f"    - ID: {user[0]}, Usuario: {user[1]}, Rol: {user[2]}")
                
        except sqlite3.OperationalError as e:
            print(f"⚠️ Error consultando usuarios: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

if __name__ == "__main__":
    verify_database()