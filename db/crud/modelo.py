from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Modelo import ModeloCreate

# MI IDEA es tener un crud por cada tabla de la base de datos y que cada uno tenga sus funciones
# por ejemplo: crud_users.py, crud_articulos.py, crud_Modelos.py, etc

#para que sirve el Session ?? https://docs.sqlalchemy.org/en/14/orm/session_api.html
def create(db: Session, descripcion: str):
    try:
        sql = text("INSERT INTO Modelos(descripcion) VALUES(:descripcion)")
        db.execute(sql.params(descripcion=descripcion))
        db.commit()
        result = db.execute(text("SELECT codigo,descripcion FROM Modelos WHERE descripcion = :descripcion"), {"descripcion": descripcion})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear la Modelo")
    
def get(db: Session, codigo: int):
    try:
        result = db.execute(text("SELECT codigo,descripcion FROM Modelos WHERE codigo = :codigo"), {"codigo": codigo})
        Modelo = result.fetchall()
        if Modelo is None:
            raise HTTPException(status_code=404, detail="Modelo no encontrada")
        return Modelo
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la Modelo")

def get_descripcion(db: Session, descripcion: str):
    try:
        result = db.execute(text("SELECT codigo FROM Modelos WHERE descripcion = :descripcion"), {"descripcion": descripcion})
        Modelo = result.fetchone()
        if Modelo is None:
            return Modelo
        else:
            raise HTTPException(status_code=404, detail=f"Modelo '{descripcion}',ya se encuentra registrada")
        a
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la Modelo")

def gets(db: Session):
    try:
        result = db.execute(text("SELECT codigo,descripcion FROM Modelos"))
        Modelos = result.fetchall()
        if not Modelos:
            raise HTTPException(status_code=404, detail="No se encontraron Modelos")
        return Modelos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudieron obtener las Modelos")
    
def update(db: Session, codigo: int, descripcion: str):
    try:
        db.execute(text("UPDATE Modelos SET descripcion = :descripcion WHERE codigo = :codigo"), {"codigo": codigo, "descripcion": descripcion})
        db.commit()
        return get(db, codigo=codigo)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar la Modelo")
    
def delete(db: Session, codigo: int):
    try:
        statement = text("DELETE FROM Modelos WHERE codigo = :codigo")
        db.execute(statement.params(codigo=codigo))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar la Modelo")
    




