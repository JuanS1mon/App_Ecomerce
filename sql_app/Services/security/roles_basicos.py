from sqlalchemy.orm import Session
try:
    from ...db.database import engine
except ImportError:
    from sql_app.db.database import engine
def init_roles():
    """Inicializa roles básicos en la base de datos"""
    db = Session(engine)
    
    # Crear roles básicos si no existen
    roles = [
        {"nombre": "admin", "descripcion": "Administrador del sistema con acceso completo"},
        {"nombre": "editor", "descripcion": "Puede crear y editar contenido"},
        {"nombre": "usuario", "descripcion": "Usuario regular con acceso básico"}
    ]
    
    for role_data in roles:
        existing_role = db.query(Role).filter(Role.nombre == role_data["nombre"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"Rol {role_data['nombre']} creado")
    
    db.commit()
    db.close()

def assign_admin_role(username):
    """Asigna el rol de admin a un usuario específico"""
    db = Session(engine)
    
    # Buscar usuario y rol admin
    user = db.query(usuarios).filter(usuarios.usuario == username).first()
    admin_role = db.query(Role).filter(Role.nombre == "admin").first()
    
    if not user:
        print(f"Usuario {username} no encontrado")
        db.close()
        return
        
    if not admin_role:
        print("Rol de admin no encontrado. Ejecute init_roles() primero.")
        db.close()
        return
    
    # Asignar rol admin al usuario
    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.commit()
        print(f"Rol admin asignado a {username}")
    else:
        print(f"El usuario {username} ya tiene el rol admin")
    
    db.close()

if __name__ == "__main__":
    init_roles()
    assign_admin_role("admin")  # Reemplaza "admin" con el nombre de tu usuario administrador