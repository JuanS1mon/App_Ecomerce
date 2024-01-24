from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.ArticulosSucursales import ArticulossucursalesCreate

def create(db: Session, ArticulosSucursales: ArticulossucursalesCreate):
    try:
        sql = text("INSERT INTO ArticulosSucursales(Articulo, Sucursal, StockMinimo, Gondola, Ruteo, Bulto, CantidadEtiquetas, ModeloEtiqueta, FechaSincro) VALUES(:Articulo, :Sucursal, :StockMinimo, :Gondola, :Ruteo, :Bulto, :CantidadEtiquetas, :ModeloEtiqueta, :FechaSincro)")
        db.execute(sql.params(ArticulosSucursales=ArticulosSucursales))
        db.commit()
        result = db.execute(text("SELECT Articulo, Sucursal, StockMinimo, Gondola, Ruteo, Bulto, CantidadEtiquetas, ModeloEtiqueta, FechaSincro FROM ArticulosSucursales WHERE Articulo = :Articulo"), {"Articulo": ArticulosSucursales.Articulo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el ArticulosSucursales")

def get(db: Session, Articulo: INTEGER):
    try:
        result = db.execute(text("SELECT Articulo, Sucursal, StockMinimo, Gondola, Ruteo, Bulto, CantidadEtiquetas, ModeloEtiqueta, FechaSincro FROM ArticulosSucursales WHERE Articulo = :Articulo"), {"Articulo": Articulo})
        ArticulosSucursales = result.fetchall()
        if ArticulosSucursales is None:
            raise HTTPException(status_code=404, detail="Articulossucursales no encontrado")
        return ArticulosSucursales
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el ArticulosSucursales")
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

