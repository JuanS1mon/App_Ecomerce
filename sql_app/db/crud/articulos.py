
from sqlalchemy.orm import Session
from sqlalchemy import text


def get_articulos(db: Session): # Esta función trae todos los usuarios
    result = db.execute(text("SELECT * FROM articulos_nene"))
    return result.fetchall()