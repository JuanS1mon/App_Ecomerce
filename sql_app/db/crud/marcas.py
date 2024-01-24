from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.marcas import MarcaCreate

# MI IDEA es tener un crud por cada tabla de la base de datos y que cada uno tenga sus funciones
# por ejemplo: crud_users.py, crud_articulos.py, crud_marcas.py, etc

#para que sirve el Session ?? https://docs.sqlalchemy.org/en/14/orm/session_api.html
def create(db: Session, descripcion: str):
    try:
        sql = text("INSERT INTO marcas(descripcion) VALUES(:descripcion)")
        db.execute(sql.params(descripcion=descripcion))
        db.commit()
        result = db.execute(text("SELECT codigo,descripcion FROM marcas WHERE descripcion = :descripcion"), {"descripcion": descripcion})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear la marca")
    
def get(db: Session, codigo: int):
    try:
        result = db.execute(text("SELECT codigo,descripcion FROM marcas WHERE codigo = :codigo"), {"codigo": codigo})
        marca = result.fetchall()
        if marca is None:
            raise HTTPException(status_code=404, detail="Marca no encontrada")
        return marca
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la marca")

def get_descripcion(db: Session, descripcion: str):
    try:
        result = db.execute(text("SELECT codigo FROM marcas WHERE descripcion = :descripcion"), {"descripcion": descripcion})
        marca = result.fetchone()
        if marca is None:
            return marca
        else:
            raise HTTPException(status_code=404, detail=f"Marca '{descripcion}',ya se encuentra registrada")
        a
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la marca")

def gets(db: Session):
    try:
        result = db.execute(text("SELECT codigo,descripcion FROM marcas"))
        marcas = result.fetchall()
        if not marcas:
            raise HTTPException(status_code=404, detail="No se encontraron marcas")
        return marcas
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudieron obtener las marcas")
    
def update(db: Session, codigo: int, descripcion: str):
    try:
        db.execute(text("UPDATE marcas SET descripcion = :descripcion WHERE codigo = :codigo"), {"codigo": codigo, "descripcion": descripcion})
        db.commit()
        return get(db, codigo=codigo)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar la marca")
    
def delete(db: Session, codigo: int):
    try:
        statement = text("DELETE FROM Marcas WHERE codigo = :codigo")
        db.execute(statement.params(codigo=codigo))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar la marca")
    




