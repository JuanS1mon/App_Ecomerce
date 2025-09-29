#!/usr/bin/env python3
"""Script para crear usuario test directamente en la base de datos"""

import sqlite3
import bcrypt
import sys
import os

def crear_usuario_test():
    """Crear usuario test en la base de datos"""
    db_path = "sql_app.db"
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("👤 === CREANDO USUARIO TEST ===")
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT codigo FROM Usuarios WHERE usuario = 'test'")
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            print(f"✅ Usuario 'test' ya existe con ID: {usuario_existente[0]}")
            user_id = usuario_existente[0]
        else:
            # Crear el usuario test
            password = "test123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO Usuarios (usuario, nombre, mail, clave, activo)
                VALUES ('test', 'Usuario Test', 'test@example.com', ?, 1)
            """, (hashed_password,))
            
            user_id = cursor.lastrowid
            print(f"✅ Usuario 'test' creado con ID: {user_id}")
        
        # Verificar roles disponibles
        cursor.execute("SELECT id, nombre FROM Roles")
        roles_disponibles = cursor.fetchall()
        print(f"📋 Roles disponibles: {roles_disponibles}")
        
        # Limpiar roles existentes del usuario test
        cursor.execute("DELETE FROM usuario_roles WHERE usuario_id = ?", (user_id,))
        print("🧹 Roles anteriores eliminados")
        
        # Asignar rol 'usuario' por defecto
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'usuario'")
        rol_usuario = cursor.fetchone()
        
        if rol_usuario:
            cursor.execute("INSERT INTO usuario_roles (usuario_id, rol_id) VALUES (?, ?)", 
                         (user_id, rol_usuario[0]))
            print(f"✅ Rol 'usuario' asignado al usuario test")
        
        conn.commit()
        
        # Verificar la creación
        cursor.execute("""
            SELECT u.codigo, u.usuario, u.nombre, r.nombre as rol
            FROM Usuarios u
            LEFT JOIN usuario_roles ur ON u.codigo = ur.usuario_id
            LEFT JOIN Roles r ON ur.rol_id = r.id
            WHERE u.usuario = 'test'
        """)
        
        resultado = cursor.fetchall()
        print(f"🔍 Usuario creado verificado: {resultado}")
        
        conn.close()
        return user_id
        
    except Exception as e:
        print(f"❌ Error creando usuario test: {e}")
        return False

if __name__ == "__main__":
    user_id = crear_usuario_test()
    if user_id:
        print(f"""
🎉 ¡Usuario test creado exitosamente!

📝 Datos del usuario:
- Usuario: test
- Contraseña: test123
- ID: {user_id}
- Rol inicial: usuario

🧪 Para probar:
1. Accede al dashboard: http://localhost:8000/usuarios_admin/?token=TU_TOKEN
2. Ve a la pestaña "Usuarios"
3. Busca el usuario "test"
4. Haz clic en el botón de editar roles (icono de etiqueta)
5. Cambia su rol de "usuario" a "manager" o "tecnico"
6. Verifica que el cambio se refleje en la tabla
        """)
    else:
        print("❌ No se pudo crear el usuario test")