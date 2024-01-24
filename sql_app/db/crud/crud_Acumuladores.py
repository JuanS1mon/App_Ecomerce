from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Acumuladores import AcumuladoresCreate

def create(db: Session, Acumuladores: AcumuladoresCreate):
    try:
        sql = text("INSERT INTO Acumuladores(Codigo, Descripcion, Tipo, Acumulador, Moneda, Transmitido) VALUES(:Codigo, :Descripcion, :Tipo, :Acumulador, :Moneda, :Transmitido)")
        db.execute(sql.params(Acumuladores=Acumuladores))
        db.commit()
        result = db.execute(text("SELECT Codigo, Descripcion, Tipo, Acumulador, Moneda, Transmitido FROM Acumuladores WHERE Codigo = :Codigo"), {"Codigo": Acumuladores.Codigo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Acumuladores")

def get(db: Session, Codigo: INTEGER):
    try:
        result = db.execute(text("SELECT Codigo, Descripcion, Tipo, Acumulador, Moneda, Transmitido FROM Acumuladores WHERE Codigo = :Codigo"), {"Codigo": Codigo})
        Acumuladores = result.fetchall()
        if Acumuladores is None:
            raise HTTPException(status_code=404, detail="Acumuladores no encontrado")
        return Acumuladores
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Acumuladores")
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

