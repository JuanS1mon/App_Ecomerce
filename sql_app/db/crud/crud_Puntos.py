from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Puntos import PuntosCreate

def create(db: Session, Puntos: PuntosCreate):
    try:
        sql = text("INSERT INTO Puntos(Sucursal, Cliente, Fecha, TipoCbte, PV, NroCbte, Puntos) VALUES(:Sucursal, :Cliente, :Fecha, :TipoCbte, :PV, :NroCbte, :Puntos)")
        db.execute(sql.params(Puntos=Puntos))
        db.commit()
        result = db.execute(text("SELECT Sucursal, Cliente, Fecha, TipoCbte, PV, NroCbte, Puntos FROM Puntos WHERE Sucursal = :Sucursal"), {"Sucursal": Puntos.Sucursal})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Puntos")

def get(db: Session, Sucursal: INTEGER):
    try:
        result = db.execute(text("SELECT Sucursal, Cliente, Fecha, TipoCbte, PV, NroCbte, Puntos FROM Puntos WHERE Sucursal = :Sucursal"), {"Sucursal": Sucursal})
        Puntos = result.fetchall()
        if Puntos is None:
            raise HTTPException(status_code=404, detail="Puntos no encontrado")
        return Puntos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Puntos")
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

