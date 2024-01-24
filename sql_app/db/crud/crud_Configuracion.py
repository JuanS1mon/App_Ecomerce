from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Configuracion import ConfiguracionCreate

def create(db: Session, Configuracion: ConfiguracionCreate):
    try:
        sql = text("INSERT INTO Configuracion(Sucursal, CuentaCobranza, Modo, PuertoRecibo, PuertoListados, LineasPorPagina) VALUES(:Sucursal, :CuentaCobranza, :Modo, :PuertoRecibo, :PuertoListados, :LineasPorPagina)")
        db.execute(sql.params(Configuracion=Configuracion))
        db.commit()
        result = db.execute(text("SELECT Sucursal, CuentaCobranza, Modo, PuertoRecibo, PuertoListados, LineasPorPagina FROM Configuracion WHERE Sucursal = :Sucursal"), {"Sucursal": Configuracion.Sucursal})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Configuracion")

def get(db: Session, Sucursal: SMALLINT):
    try:
        result = db.execute(text("SELECT Sucursal, CuentaCobranza, Modo, PuertoRecibo, PuertoListados, LineasPorPagina FROM Configuracion WHERE Sucursal = :Sucursal"), {"Sucursal": Sucursal})
        Configuracion = result.fetchall()
        if Configuracion is None:
            raise HTTPException(status_code=404, detail="Configuracion no encontrado")
        return Configuracion
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Configuracion")
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

