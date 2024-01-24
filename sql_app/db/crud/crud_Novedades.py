from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Novedades import NovedadesCreate

def create(db: Session, Novedades: NovedadesCreate):
    try:
        sql = text("INSERT INTO Novedades(Fecha, Sucursal, Articulo, Campo, Hora, PrecioAnt, PrecioNuevo, Transmitido, TasaIva, Usuario) VALUES(:Fecha, :Sucursal, :Articulo, :Campo, :Hora, :PrecioAnt, :PrecioNuevo, :Transmitido, :TasaIva, :Usuario)")
        db.execute(sql.params(Novedades=Novedades))
        db.commit()
        result = db.execute(text("SELECT Fecha, Sucursal, Articulo, Campo, Hora, PrecioAnt, PrecioNuevo, Transmitido, TasaIva, Usuario FROM Novedades WHERE Fecha = :Fecha"), {"Fecha": Novedades.Fecha})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Novedades")

def get(db: Session, Fecha: DATETIME):
    try:
        result = db.execute(text("SELECT Fecha, Sucursal, Articulo, Campo, Hora, PrecioAnt, PrecioNuevo, Transmitido, TasaIva, Usuario FROM Novedades WHERE Fecha = :Fecha"), {"Fecha": Fecha})
        Novedades = result.fetchall()
        if Novedades is None:
            raise HTTPException(status_code=404, detail="Novedades no encontrado")
        return Novedades
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Novedades")
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

