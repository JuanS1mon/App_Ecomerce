from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.InventariosArticulos import InventariosarticulosCreate

def create(db: Session, InventariosArticulos: InventariosarticulosCreate):
    try:
        sql = text("INSERT INTO InventariosArticulos(Fecha, Sucursal, Inventario, Articulo, Cantidad, StockAnterior, FechaCarga) VALUES(:Fecha, :Sucursal, :Inventario, :Articulo, :Cantidad, :StockAnterior, :FechaCarga)")
        db.execute(sql.params(InventariosArticulos=InventariosArticulos))
        db.commit()
        result = db.execute(text("SELECT Fecha, Sucursal, Inventario, Articulo, Cantidad, StockAnterior, FechaCarga FROM InventariosArticulos WHERE Fecha = :Fecha"), {"Fecha": InventariosArticulos.Fecha})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el InventariosArticulos")

def get(db: Session, Fecha: SMALLDATETIME):
    try:
        result = db.execute(text("SELECT Fecha, Sucursal, Inventario, Articulo, Cantidad, StockAnterior, FechaCarga FROM InventariosArticulos WHERE Fecha = :Fecha"), {"Fecha": Fecha})
        InventariosArticulos = result.fetchall()
        if InventariosArticulos is None:
            raise HTTPException(status_code=404, detail="Inventariosarticulos no encontrado")
        return InventariosArticulos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el InventariosArticulos")
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

