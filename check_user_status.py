from sql_app.db.database import get_db
from sql_app.db.models.config.usuarios import Usuarios

def check_user_status():
    print("Iniciando verificación del usuario 'juan'...")
    try:
        db = next(get_db())  # Obtener la sesión de base de datos
        user = db.query(Usuarios).filter(Usuarios.usuario == 'juan').first()
        if user:
            print(f"Usuario encontrado: {user.usuario}, Activo: {user.activo}")
        else:
            print("Usuario 'juan' no encontrado.")
    except Exception as e:
        print(f"Error al verificar el usuario: {str(e)}")

if __name__ == "__main__":
    check_user_status()
