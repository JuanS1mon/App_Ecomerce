from sql_app.db.database import SessionLocal
from sql_app.Services.security.utils import encriptar_clave
from sql_app.models import User  # Asegúrate de que este modelo esté definido correctamente

def update_admin_password(new_password: str):
    """Actualiza la contraseña del usuario admin."""
    db = SessionLocal()
    try:
        # Busca al usuario admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Usuario admin no encontrado.")
            return

        # Genera el hash de la nueva contraseña
        hashed_password = encriptar_clave(new_password)

        # Actualiza la contraseña
        admin_user.password = hashed_password
        db.commit()
        print("Contraseña del usuario admin actualizada correctamente.")
    except Exception as e:
        print(f"Error al actualizar la contraseña: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_password("123")
