#!/usr/bin/env python3
"""
Script para asignar rol admin al usuario juan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import engine
from sqlalchemy import text

def assign_admin_role():
    try:
        with engine.connect() as conn:
            # Verificar si ya existe la asignación
            result = conn.execute(text("""
                SELECT 1 FROM UsuariosRol
                WHERE usuario_id = (SELECT codigo FROM Usuarios WHERE usuario = 'juan')
                AND rol_id = (SELECT id FROM Roles WHERE nombre = 'admin')
            """))
            exists = result.fetchone()

            if exists:
                print("El usuario 'juan' ya tiene el rol 'admin' asignado.")
                return

            # Insertar la asignación
            conn.execute(text("""
                INSERT INTO UsuariosRol (usuario_id, rol_id)
                SELECT u.codigo, r.id
                FROM Usuarios u, Roles r
                WHERE u.usuario = 'juan' AND r.nombre = 'admin'
            """))
            conn.commit()
            print("Rol 'admin' asignado exitosamente al usuario 'juan'.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    assign_admin_role()