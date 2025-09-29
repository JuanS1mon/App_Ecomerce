#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar la carga de roles del usuario juan
"""

import sqlite3
import sys
import os

# Agregar el directorio raíz al path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_juan_roles():
    """Diagnostica los roles del usuario juan"""
    
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    print("=== DIAGNÓSTICO DE ROLES DEL USUARIO JUAN ===")
    
    try:
        # 1. Verificar usuario juan
        cursor.execute("SELECT codigo, usuario, nombre, activo FROM Usuarios WHERE usuario = 'juan'")
        user_info = cursor.fetchone()
        
        if user_info:
            user_id, username, nombre, activo = user_info
            print(f"✅ Usuario encontrado:")
            print(f"   ID: {user_id}")
            print(f"   Usuario: {username}")
            print(f"   Nombre: {nombre}")
            print(f"   Activo: {activo}")
        else:
            print("❌ Usuario 'juan' no encontrado")
            return
            
        # 2. Verificar roles disponibles
        cursor.execute("SELECT id, nombre, descripcion FROM Roles")
        roles = cursor.fetchall()
        print(f"\n✅ Roles disponibles ({len(roles)}):")
        for role_id, role_name, role_desc in roles:
            print(f"   {role_id}: {role_name} - {role_desc}")
            
        # 3. Verificar relaciones usuario-rol
        cursor.execute("SELECT usuario_id, rol_id FROM usuario_roles WHERE usuario_id = ?", (user_id,))
        user_roles = cursor.fetchall()
        print(f"\n✅ Relaciones usuario-rol para juan ({len(user_roles)}):")
        for ur_user_id, ur_role_id in user_roles:
            print(f"   Usuario ID: {ur_user_id}, Rol ID: {ur_role_id}")
            
        # 4. Query completa JOIN para verificar roles asignados
        cursor.execute("""
            SELECT u.codigo, u.usuario, r.id, r.nombre, r.descripcion
            FROM Usuarios u
            JOIN usuario_roles ur ON u.codigo = ur.usuario_id
            JOIN Roles r ON ur.rol_id = r.id
            WHERE u.usuario = 'juan'
        """)
        
        role_assignments = cursor.fetchall()
        print(f"\n✅ Roles asignados a juan (JOIN query - {len(role_assignments)}):")
        for user_code, username, role_id, role_name, role_desc in role_assignments:
            print(f"   {role_name} (ID: {role_id}): {role_desc}")
            
        # 5. Simular la query que usa la aplicación
        print(f"\n🔍 Simulando query de la aplicación:")
        cursor.execute("""
            SELECT r.nombre
            FROM Roles r
            JOIN usuario_roles ur ON r.id = ur.rol_id
            WHERE ur.usuario_id = ?
        """, (user_id,))
        
        app_roles = cursor.fetchall()
        role_names = [role[0] for role in app_roles]
        role_names_lower = [role.lower() for role in role_names]
        
        print(f"   Roles encontrados: {role_names}")
        print(f"   Roles en minúsculas: {role_names_lower}")
        print(f"   ¿Contiene 'admin'?: {'admin' in role_names_lower}")
        
        # 6. Test final
        if 'admin' in role_names_lower:
            print(f"\n✅ ¡DIAGNÓSTICO: Juan debería tener acceso de administrador!")
        else:
            print(f"\n❌ DIAGNÓSTICO: Juan NO tiene el rol 'admin' asignado")
            print(f"   Roles asignados: {role_names_lower}")
            
    except Exception as e:
        print(f"❌ Error durante diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_juan_roles()