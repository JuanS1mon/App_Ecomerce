from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Empresas import EmpresasCreate

def create(db: Session, Empresas: EmpresasCreate):
    try:
        sql = text("INSERT INTO Empresas(Numero, Nombre, CUIT, Activa, EjercicioActual, FechaCierreCaja, Logo, RazonSocial, Direccion, NroAgRet, OrdenPago, R_IIBB, MontoIIBB, R_gan, TasaGan, OPCant, RetCant, BaseGan, FechaCierreIva, FechaProximoCierreIva, TipoOrdenPago, Color, FormatoRecibo, FechaCierreBancos, PathOP, PathRET, PercibeIIBBenDP, Localidad, PathLogoOP, AFIP_URLTFA, AFIP_URLPFX, PuntoVentaComision, PuertoImpresionDP, R_IIBBAGIP, NroAgRetAGIP, R_APR, NroAgRetIIBB, NroAgRetAPR, MontoAPR, PuntoVentaAplicacionComision, BancoDefecto) VALUES(:Numero, :Nombre, :CUIT, :Activa, :EjercicioActual, :FechaCierreCaja, :Logo, :RazonSocial, :Direccion, :NroAgRet, :OrdenPago, :R_IIBB, :MontoIIBB, :R_gan, :TasaGan, :OPCant, :RetCant, :BaseGan, :FechaCierreIva, :FechaProximoCierreIva, :TipoOrdenPago, :Color, :FormatoRecibo, :FechaCierreBancos, :PathOP, :PathRET, :PercibeIIBBenDP, :Localidad, :PathLogoOP, :AFIP_URLTFA, :AFIP_URLPFX, :PuntoVentaComision, :PuertoImpresionDP, :R_IIBBAGIP, :NroAgRetAGIP, :R_APR, :NroAgRetIIBB, :NroAgRetAPR, :MontoAPR, :PuntoVentaAplicacionComision, :BancoDefecto)")
        db.execute(sql.params(Empresas=Empresas))
        db.commit()
        result = db.execute(text("SELECT Numero, Nombre, CUIT, Activa, EjercicioActual, FechaCierreCaja, Logo, RazonSocial, Direccion, NroAgRet, OrdenPago, R_IIBB, MontoIIBB, R_gan, TasaGan, OPCant, RetCant, BaseGan, FechaCierreIva, FechaProximoCierreIva, TipoOrdenPago, Color, FormatoRecibo, FechaCierreBancos, PathOP, PathRET, PercibeIIBBenDP, Localidad, PathLogoOP, AFIP_URLTFA, AFIP_URLPFX, PuntoVentaComision, PuertoImpresionDP, R_IIBBAGIP, NroAgRetAGIP, R_APR, NroAgRetIIBB, NroAgRetAPR, MontoAPR, PuntoVentaAplicacionComision, BancoDefecto FROM Empresas WHERE Numero = :Numero"), {"Numero": Empresas.Numero})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Empresas")

def get(db: Session, Numero: INTEGER):
    try:
        result = db.execute(text("SELECT Numero, Nombre, CUIT, Activa, EjercicioActual, FechaCierreCaja, Logo, RazonSocial, Direccion, NroAgRet, OrdenPago, R_IIBB, MontoIIBB, R_gan, TasaGan, OPCant, RetCant, BaseGan, FechaCierreIva, FechaProximoCierreIva, TipoOrdenPago, Color, FormatoRecibo, FechaCierreBancos, PathOP, PathRET, PercibeIIBBenDP, Localidad, PathLogoOP, AFIP_URLTFA, AFIP_URLPFX, PuntoVentaComision, PuertoImpresionDP, R_IIBBAGIP, NroAgRetAGIP, R_APR, NroAgRetIIBB, NroAgRetAPR, MontoAPR, PuntoVentaAplicacionComision, BancoDefecto FROM Empresas WHERE Numero = :Numero"), {"Numero": Numero})
        Empresas = result.fetchall()
        if Empresas is None:
            raise HTTPException(status_code=404, detail="Empresas no encontrado")
        return Empresas
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Empresas")
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

