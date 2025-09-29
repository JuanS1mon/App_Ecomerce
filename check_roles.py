#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

print("=== ROLES DISPONIBLES ===")
try:
    cursor.execute('SELECT * FROM Roles')
    roles = cursor.fetchall()
    if roles:
        cursor.execute('PRAGMA table_info(Roles)')
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columnas: {columns}")
        for role in roles:
            print(f"  {dict(zip(columns, role))}")
    else:
        print("  No hay roles en la base de datos")
except Exception as e:
    print(f"Error al obtener roles: {e}")

print("\n=== RELACIONES USUARIO-ROL ===")
try:
    cursor.execute('SELECT * FROM usuario_roles')
    user_roles = cursor.fetchall()
    if user_roles:
        cursor.execute('PRAGMA table_info(usuario_roles)')
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columnas: {columns}")
        for ur in user_roles:
            print(f"  {dict(zip(columns, ur))}")
    else:
        print("  No hay relaciones usuario-rol en la base de datos")
except Exception as e:
    print(f"Error al obtener relaciones usuario-rol: {e}")

print("\n=== INFORMACIÓN ADICIONAL ===")
print("La base de datos parece estar inicializada pero sin datos de usuarios.")
print("Esto significa que necesitamos crear el usuario 'juan' y asignarle el rol de admin.")

conn.close()