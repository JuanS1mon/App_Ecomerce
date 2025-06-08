#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def check_users():
    """Verificar qué usuarios existen en la base de datos"""
    try:
        from sql_app.db.database import get_db, SessionLocal
        from sql_app.db.crud.config.Usuarios import gets_usuarios
        
        # Crear sesión de base de datos
        db = SessionLocal()
        
        try:
            print("🔍 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
            print("=" * 50)
            
            # Obtener todos los usuarios
            usuarios = gets_usuarios(db)
            
            if usuarios:
                print(f"📊 Se encontraron {len(usuarios)} usuario(s):")
                for usuario in usuarios:
                    print(f"  - Código: {usuario.get('codigo', 'N/A')}")
                    print(f"    Usuario: {usuario.get('usuario', 'N/A')}")
                    print(f"    Nombre: {usuario.get('nombre', 'N/A')}")
                    print(f"    Email: {usuario.get('Mail', 'N/A')}")
                    print(f"    Activo: {usuario.get('activo', 'N/A')}")
                    print("")
            else:
                print("❌ No se encontraron usuarios en la base de datos")
                print("💡 Necesitas crear un usuario administrador primero")
                
        except Exception as e:
            print(f"❌ Error consultando usuarios: {e}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

def create_admin_user():
    """Crear un usuario administrador"""
    try:
        from sql_app.db.database import SessionLocal
        from sql_app.db.crud.config.Usuarios import create_usuario
        from sql_app.Services.security.security import encriptar_clave
        
        db = SessionLocal()
        
        try:
            print("\n🔧 CREANDO USUARIO ADMINISTRADOR")
            print("=" * 40)
            
            # Encriptar la contraseña
            clave_encriptada = encriptar_clave("admin123")
            
            # Crear usuario admin
            result = create_usuario(
                db=db,
                nombre="Administrador",
                usuario="admin",
                clave=clave_encriptada,
                mail="admin@sistema.com"
            )
            
            if result:
                print("✅ Usuario administrador creado exitosamente!")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                print("   Email: admin@sistema.com")
            else:
                print("❌ Error creando usuario administrador")
                
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_users()
    
    # Preguntar si crear usuario admin
    print("\n❓ ¿Crear usuario administrador? (y/n): ", end="")
    try:
        respuesta = input().lower().strip()
        if respuesta in ['y', 'yes', 's', 'si']:
            create_admin_user()
            print("\n🔄 Verificando usuarios después de la creación:")
            check_users()
    except:
        pass
