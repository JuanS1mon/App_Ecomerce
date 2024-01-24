from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Fantasia import FantasiaCreate

def create(db: Session, Fantasia: FantasiaCreate):
    try:
        sql = text("INSERT INTO Fantasia(Sucursal, Linea, Texto, Doble) VALUES(:Sucursal, :Linea, :Texto, :Doble)")
        db.execute(sql.params(Fantasia=Fantasia))
        db.commit()
        result = db.execute(text("SELECT Sucursal, Linea, Texto, Doble FROM Fantasia WHERE Sucursal = :Sucursal"), {"Sucursal": Fantasia.Sucursal})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Fantasia")

def get(db: Session, Sucursal: INTEGER):
    try:
        result = db.execute(text("SELECT Sucursal, Linea, Texto, Doble FROM Fantasia WHERE Sucursal = :Sucursal"), {"Sucursal": Sucursal})
        Fantasia = result.fetchall()
        if Fantasia is None:
            raise HTTPException(status_code=404, detail="Fantasia no encontrado")
        return Fantasia
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Fantasia")
def get_campo(db: Session, campo: str):
    try:
        result = db.execute(text("SELECT codigo FROM marcas WHERE descripcion = :campo"), {"campo": descripcion})
        marca = result.fetchone()
        if marca is None:
            return marca
        else:
            raise HTTPException(status_code=404, detail=f"Marca '{campo}', ya se encuentra registrada")
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

