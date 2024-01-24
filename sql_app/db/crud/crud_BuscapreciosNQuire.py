from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.BuscapreciosNQuire import BuscapreciosnquireCreate

def create(db: Session, BuscapreciosNQuire: BuscapreciosnquireCreate):
    try:
        sql = text("INSERT INTO BuscapreciosNQuire(EAN, Descripcion, Marca, PresentacionCantidad, PresentacionUnidad, Precio, Oferta) VALUES(:EAN, :Descripcion, :Marca, :PresentacionCantidad, :PresentacionUnidad, :Precio, :Oferta)")
        db.execute(sql.params(BuscapreciosNQuire=BuscapreciosNQuire))
        db.commit()
        result = db.execute(text("SELECT EAN, Descripcion, Marca, PresentacionCantidad, PresentacionUnidad, Precio, Oferta FROM BuscapreciosNQuire WHERE EAN = :EAN"), {"EAN": BuscapreciosNQuire.EAN})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el BuscapreciosNQuire")

def get(db: Session, EAN: MONEY):
    try:
        result = db.execute(text("SELECT EAN, Descripcion, Marca, PresentacionCantidad, PresentacionUnidad, Precio, Oferta FROM BuscapreciosNQuire WHERE EAN = :EAN"), {"EAN": EAN})
        BuscapreciosNQuire = result.fetchall()
        if BuscapreciosNQuire is None:
            raise HTTPException(status_code=404, detail="Buscapreciosnquire no encontrado")
        return BuscapreciosNQuire
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el BuscapreciosNQuire")
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

