from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Proveedores import ProveedoresCreate

def create(db: Session, Proveedores: ProveedoresCreate):
    try:
        sql = text("INSERT INTO Proveedores(Codigo, Nombre, RazonSocial, CUIT, Direccion, Localidad, Telefono, Telefono2, Fax, Contacto, R_IIBB, RetieneGanancias, NroIIBB, Email, PaginaWeb, ReferenciaProv, CuentaProveedor, CuentaAsignacion, TipoIVA, Celular, Rubro, HorarioAtencion, FormaPago, CUITLibre, Habilitado, Transmitido, CodigoPostal, ContactoDireccion, ContactoTelefono, ContactoEmail, FechaAlta, Observacion, EsAgenteRetencion, R_IIBBAGIP, R_APR, FormatoRecepcion, CargaCbteGeneraDP, DiasBloqueoPagoPreDP) VALUES(:Codigo, :Nombre, :RazonSocial, :CUIT, :Direccion, :Localidad, :Telefono, :Telefono2, :Fax, :Contacto, :R_IIBB, :RetieneGanancias, :NroIIBB, :Email, :PaginaWeb, :ReferenciaProv, :CuentaProveedor, :CuentaAsignacion, :TipoIVA, :Celular, :Rubro, :HorarioAtencion, :FormaPago, :CUITLibre, :Habilitado, :Transmitido, :CodigoPostal, :ContactoDireccion, :ContactoTelefono, :ContactoEmail, :FechaAlta, :Observacion, :EsAgenteRetencion, :R_IIBBAGIP, :R_APR, :FormatoRecepcion, :CargaCbteGeneraDP, :DiasBloqueoPagoPreDP)")
        db.execute(sql.params(Proveedores=Proveedores))
        db.commit()
        result = db.execute(text("SELECT Codigo, Nombre, RazonSocial, CUIT, Direccion, Localidad, Telefono, Telefono2, Fax, Contacto, R_IIBB, RetieneGanancias, NroIIBB, Email, PaginaWeb, ReferenciaProv, CuentaProveedor, CuentaAsignacion, TipoIVA, Celular, Rubro, HorarioAtencion, FormaPago, CUITLibre, Habilitado, Transmitido, CodigoPostal, ContactoDireccion, ContactoTelefono, ContactoEmail, FechaAlta, Observacion, EsAgenteRetencion, R_IIBBAGIP, R_APR, FormatoRecepcion, CargaCbteGeneraDP, DiasBloqueoPagoPreDP FROM Proveedores WHERE Codigo = :Codigo"), {"Codigo": Proveedores.Codigo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Proveedores")

def get(db: Session, Codigo: INTEGER):
    try:
        result = db.execute(text("SELECT Codigo, Nombre, RazonSocial, CUIT, Direccion, Localidad, Telefono, Telefono2, Fax, Contacto, R_IIBB, RetieneGanancias, NroIIBB, Email, PaginaWeb, ReferenciaProv, CuentaProveedor, CuentaAsignacion, TipoIVA, Celular, Rubro, HorarioAtencion, FormaPago, CUITLibre, Habilitado, Transmitido, CodigoPostal, ContactoDireccion, ContactoTelefono, ContactoEmail, FechaAlta, Observacion, EsAgenteRetencion, R_IIBBAGIP, R_APR, FormatoRecepcion, CargaCbteGeneraDP, DiasBloqueoPagoPreDP FROM Proveedores WHERE Codigo = :Codigo"), {"Codigo": Codigo})
        Proveedores = result.fetchall()
        if Proveedores is None:
            raise HTTPException(status_code=404, detail="Proveedores no encontrado")
        return Proveedores
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Proveedores")
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

