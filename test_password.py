#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar directamente la verificación de contraseñas
"""

import sqlite3
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sql_app.Services.security.security import verificar_clave

def test_password_verification():
    """Prueba la verificación de contraseñas directamente"""
    
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    print("=== PRUEBA DE VERIFICACIÓN DE CONTRASEÑAS ===")
    
    try:
        # Obtener el hash de la contraseña de juan
        cursor.execute("SELECT usuario, clave FROM Usuarios WHERE usuario = 'juan'")
        result = cursor.fetchone()
        
        if result:
            username, stored_hash = result
            print(f"Usuario: {username}")
            print(f"Hash almacenado: {stored_hash}")
            print(f"Longitud del hash: {len(stored_hash)}")
            
            # Probar la verificación con la contraseña correcta
            password_test = "admin123"
            is_valid = verificar_clave(password_test, stored_hash)
            
            print(f"\nPrueba de verificación:")
            print(f"Contraseña de prueba: '{password_test}'")
            print(f"Resultado de verificación: {is_valid}")
            
            if is_valid:
                print("✅ La verificación de contraseña funciona correctamente")
            else:
                print("❌ La verificación de contraseña está fallando")
                
                # Probar con otras contraseñas posibles
                other_passwords = ["admin", "123", "juan", "password"]
                print("\nProbando otras contraseñas posibles:")
                for pwd in other_passwords:
                    result = verificar_clave(pwd, stored_hash)
                    print(f"  '{pwd}': {result}")
                    
        else:
            print("❌ Usuario 'juan' no encontrado en la base de datos")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_password_verification()