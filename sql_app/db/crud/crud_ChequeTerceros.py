from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.ChequeTerceros import ChequetercerosCreate

def create(db: Session, ChequeTerceros: ChequetercerosCreate):
    try:
        sql = text("INSERT INTO ChequeTerceros(Empresa, Cliente, Emisor, NroCheque, Banco, Importe, FechaVencimiento, FechaEmision, FechaRecepcion, FechaEntrega, TipoDestino, CodigoDestino, CbteDestino, Detalle, TipoOrigen, CodigoOrigen, Anulado, Sucursal, OrdenCarga, ClearingHoras) VALUES(:Empresa, :Cliente, :Emisor, :NroCheque, :Banco, :Importe, :FechaVencimiento, :FechaEmision, :FechaRecepcion, :FechaEntrega, :TipoDestino, :CodigoDestino, :CbteDestino, :Detalle, :TipoOrigen, :CodigoOrigen, :Anulado, :Sucursal, :OrdenCarga, :ClearingHoras)")
        db.execute(sql.params(ChequeTerceros=ChequeTerceros))
        db.commit()
        result = db.execute(text("SELECT Empresa, Cliente, Emisor, NroCheque, Banco, Importe, FechaVencimiento, FechaEmision, FechaRecepcion, FechaEntrega, TipoDestino, CodigoDestino, CbteDestino, Detalle, TipoOrigen, CodigoOrigen, Anulado, Sucursal, OrdenCarga, ClearingHoras FROM ChequeTerceros WHERE Empresa = :Empresa"), {"Empresa": ChequeTerceros.Empresa})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el ChequeTerceros")

def get(db: Session, Empresa: INTEGER):
    try:
        result = db.execute(text("SELECT Empresa, Cliente, Emisor, NroCheque, Banco, Importe, FechaVencimiento, FechaEmision, FechaRecepcion, FechaEntrega, TipoDestino, CodigoDestino, CbteDestino, Detalle, TipoOrigen, CodigoOrigen, Anulado, Sucursal, OrdenCarga, ClearingHoras FROM ChequeTerceros WHERE Empresa = :Empresa"), {"Empresa": Empresa})
        ChequeTerceros = result.fetchall()
        if ChequeTerceros is None:
            raise HTTPException(status_code=404, detail="Chequeterceros no encontrado")
        return ChequeTerceros
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el ChequeTerceros")
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

