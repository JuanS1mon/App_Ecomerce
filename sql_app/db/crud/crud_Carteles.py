from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Carteles import CartelesCreate

def create(db: Session, Carteles: CartelesCreate):
    try:
        sql = text("INSERT INTO Carteles(Cartel, Fecha, Color, X, Y, Alto, Ancho, Texto, Usuario, Anulado, FechaFin) VALUES(:Cartel, :Fecha, :Color, :X, :Y, :Alto, :Ancho, :Texto, :Usuario, :Anulado, :FechaFin)")
        db.execute(sql.params(Carteles=Carteles))
        db.commit()
        result = db.execute(text("SELECT Cartel, Fecha, Color, X, Y, Alto, Ancho, Texto, Usuario, Anulado, FechaFin FROM Carteles WHERE Cartel = :Cartel"), {"Cartel": Carteles.Cartel})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Carteles")

def get(db: Session, Cartel: INTEGER):
    try:
        result = db.execute(text("SELECT Cartel, Fecha, Color, X, Y, Alto, Ancho, Texto, Usuario, Anulado, FechaFin FROM Carteles WHERE Cartel = :Cartel"), {"Cartel": Cartel})
        Carteles = result.fetchall()
        if Carteles is None:
            raise HTTPException(status_code=404, detail="Carteles no encontrado")
        return Carteles
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Carteles")
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

