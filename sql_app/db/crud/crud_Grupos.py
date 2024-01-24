from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Grupos import GruposCreate

def create(db: Session, Grupos: GruposCreate):
    try:
        sql = text("INSERT INTO Grupos(Codigo, Descripcion, DiasVencimiento, TasaDiaria, FechaProximoCorte, FinMes, Transmitido) VALUES(:Codigo, :Descripcion, :DiasVencimiento, :TasaDiaria, :FechaProximoCorte, :FinMes, :Transmitido)")
        db.execute(sql.params(Grupos=Grupos))
        db.commit()
        result = db.execute(text("SELECT Codigo, Descripcion, DiasVencimiento, TasaDiaria, FechaProximoCorte, FinMes, Transmitido FROM Grupos WHERE Codigo = :Codigo"), {"Codigo": Grupos.Codigo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Grupos")

def get(db: Session, Codigo: SMALLINT):
    try:
        result = db.execute(text("SELECT Codigo, Descripcion, DiasVencimiento, TasaDiaria, FechaProximoCorte, FinMes, Transmitido FROM Grupos WHERE Codigo = :Codigo"), {"Codigo": Codigo})
        Grupos = result.fetchall()
        if Grupos is None:
            raise HTTPException(status_code=404, detail="Grupos no encontrado")
        return Grupos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Grupos")
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

