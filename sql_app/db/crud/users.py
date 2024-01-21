from sqlalchemy.orm import Session
from sqlalchemy import text

from ..schemas.user import UserCreate

# MI IDEA es tener un crud por cada tabla de la base de datos y que cada uno tenga sus funciones
# por ejemplo: crud_users.py, crud_articulos.py, crud_marcas.py, etc

# CRUD de usuarios
#Faltan los Try y los Except

#para que sirve el Session ?? https://docs.sqlalchemy.org/en/14/orm/session_api.html

def get_user(db: Session, user_id: int): # Esta función trae un usuario por su id
    statement = text("SELECT * FROM users WHERE id = :user_id")
    result = db.execute(statement.params(user_id=user_id))
    return result.first()

def get_user_by_email(db: Session, email: str): #esta función busca un usuario por su email
    statement = text("SELECT * FROM users WHERE email = :email")
    result = db.execute(statement.params(email=email))
    return result.first()



def get_users(db: Session): # Esta función trae todos los usuarios
    result = db.execute(text("SELECT * FROM users"))
    return result.fetchall()


def create_user(db: Session, user: UserCreate):# Esta función crea un usuario
    # Define un valor predeterminado para is_active
    is_active = user.is_active if user.is_active is not None else False

    # Incluye is_active en la consulta de inserción no me andaba sin eso. 
    statement = text("INSERT INTO users(email, hashed_password, is_active) VALUES(:email, :hashed_password, :is_active)")

    db.execute(statement.params(email=user.email, hashed_password=user.hashed_password, is_active=is_active))
    db.commit()

    # Obtener el usuario que acaba de ser creado , podria ejectura get_user_by_email
    result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": user.email})
    return result.fetchone()


def delete_user(db: Session, user_id: int): # Esta función elimina un usuario
    statement = text("DELETE FROM users WHERE id = :user_id")
    db.execute(statement.params(user_id=user_id))
    db.commit()

def update_user(db: Session, user_id: int, user: UserCreate): # Esta función actualiza un usuario
    # Crear la consulta de actualización
    statement = text("UPDATE users SET email = :email, hashed_password = :hashed_password, is_active = :is_active WHERE id = :user_id")

    # Ejecutar la consulta de actualización
    db.execute(statement.params(email=user.email, hashed_password=user.hashed_password, is_active=user.is_active, user_id=user_id))
    db.commit()# Guardar los cambios en la base de datos

    # Obtener el usuario que acaba de ser actualizado
    result = db.execute(text("SELECT * FROM users WHERE id = :user_id"), {"user_id": user_id})
    return result.fetchone()