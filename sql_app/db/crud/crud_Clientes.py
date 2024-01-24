from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Clientes import ClientesCreate

def create(db: Session, Clientes: ClientesCreate):
    try:
        sql = text("INSERT INTO Clientes(Sucursal, Codigo, Grupo, Nombre, RazonSocial, Tarjeta, Categoria, TipoIva, Documento, Credito, FechaVencTarjeta, FechaAlta, Estado, Transmitido, IIBB, Vendedor, FormaPago, ListaPrecio, Descuento, CreditoCuotas, TipoDocumento, Repartidor, Cobrador, Rubro, CargoAdministrativo, Observacion, VtoCUIT, PercepcionIIBB, Abasto, OrdenZona, DiasToleranciaVto, SumaPuntos, PercepcionIIBBAGIP, PercepcionAPR, EsAgenteRetencionIVA, Comision, Clave, TipoPeriodo, ImporteDescuentoMaximoPromociones) VALUES(:Sucursal, :Codigo, :Grupo, :Nombre, :RazonSocial, :Tarjeta, :Categoria, :TipoIva, :Documento, :Credito, :FechaVencTarjeta, :FechaAlta, :Estado, :Transmitido, :IIBB, :Vendedor, :FormaPago, :ListaPrecio, :Descuento, :CreditoCuotas, :TipoDocumento, :Repartidor, :Cobrador, :Rubro, :CargoAdministrativo, :Observacion, :VtoCUIT, :PercepcionIIBB, :Abasto, :OrdenZona, :DiasToleranciaVto, :SumaPuntos, :PercepcionIIBBAGIP, :PercepcionAPR, :EsAgenteRetencionIVA, :Comision, :Clave, :TipoPeriodo, :ImporteDescuentoMaximoPromociones)")
        db.execute(sql.params(Clientes=Clientes))
        db.commit()
        result = db.execute(text("SELECT Sucursal, Codigo, Grupo, Nombre, RazonSocial, Tarjeta, Categoria, TipoIva, Documento, Credito, FechaVencTarjeta, FechaAlta, Estado, Transmitido, IIBB, Vendedor, FormaPago, ListaPrecio, Descuento, CreditoCuotas, TipoDocumento, Repartidor, Cobrador, Rubro, CargoAdministrativo, Observacion, VtoCUIT, PercepcionIIBB, Abasto, OrdenZona, DiasToleranciaVto, SumaPuntos, PercepcionIIBBAGIP, PercepcionAPR, EsAgenteRetencionIVA, Comision, Clave, TipoPeriodo, ImporteDescuentoMaximoPromociones FROM Clientes WHERE Sucursal = :Sucursal"), {"Sucursal": Clientes.Sucursal})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Clientes")

def get(db: Session, Sucursal: INTEGER):
    try:
        result = db.execute(text("SELECT Sucursal, Codigo, Grupo, Nombre, RazonSocial, Tarjeta, Categoria, TipoIva, Documento, Credito, FechaVencTarjeta, FechaAlta, Estado, Transmitido, IIBB, Vendedor, FormaPago, ListaPrecio, Descuento, CreditoCuotas, TipoDocumento, Repartidor, Cobrador, Rubro, CargoAdministrativo, Observacion, VtoCUIT, PercepcionIIBB, Abasto, OrdenZona, DiasToleranciaVto, SumaPuntos, PercepcionIIBBAGIP, PercepcionAPR, EsAgenteRetencionIVA, Comision, Clave, TipoPeriodo, ImporteDescuentoMaximoPromociones FROM Clientes WHERE Sucursal = :Sucursal"), {"Sucursal": Sucursal})
        Clientes = result.fetchall()
        if Clientes is None:
            raise HTTPException(status_code=404, detail="Clientes no encontrado")
        return Clientes
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Clientes")
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

