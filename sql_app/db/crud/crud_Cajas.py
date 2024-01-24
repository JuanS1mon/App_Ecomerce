from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Cajas import CajasCreate

def create(db: Session, Cajas: CajasCreate):
    try:
        sql = text("INSERT INTO Cajas(Sucursal, Caja, PuntoVenta, Estado, PuertoComunica, PuertoArchivo, Direccion, Empresa) VALUES(:Sucursal, :Caja, :PuntoVenta, :Estado, :PuertoComunica, :PuertoArchivo, :Direccion, :Empresa)")
        db.execute(sql.params(Cajas=Cajas))
        db.commit()
        result = db.execute(text("SELECT Sucursal, Caja, PuntoVenta, Estado, PuertoComunica, PuertoArchivo, Direccion, Empresa FROM Cajas WHERE Sucursal = :Sucursal"), {"Sucursal": Cajas.Sucursal})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Cajas")

def get(db: Session, Sucursal: INTEGER):
    try:
        result = db.execute(text("SELECT Sucursal, Caja, PuntoVenta, Estado, PuertoComunica, PuertoArchivo, Direccion, Empresa FROM Cajas WHERE Sucursal = :Sucursal"), {"Sucursal": Sucursal})
        Cajas = result.fetchall()
        if Cajas is None:
            raise HTTPException(status_code=404, detail="Cajas no encontrado")
        return Cajas
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Cajas")
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

