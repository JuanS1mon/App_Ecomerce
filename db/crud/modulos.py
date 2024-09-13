
from sqlalchemy.orm import Session
from sqlalchemy import text


def gets(db: Session): # Esta función trae todos los usuarios
    result = db.execute(text("SELECT descripcion,ejecutable FROM modulos where codigo between 1 and 50 "))
    return result.fetchall()