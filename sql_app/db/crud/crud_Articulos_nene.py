from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Articulos_nene import Articulos_neneCreate

def create(db: Session, Articulos_nene: Articulos_neneCreate):
    try:
        sql = text("INSERT INTO Articulos_nene(Codigo, EAN, Descripcion, DescripcionCorta, PrecioCosto, PrecioVenta, Margen, IVA, EsCombo, Proveedor, Departamento, Marca, Familia, UxB, HabilCajas, HabilEstad, HabilStock, HabilOC, HabilBalanzas, BalDiasVto, BalCodigo, Tipo, CodigoEnvase, FechaModificacion, FechaAlta, HoraModificacion, Transmitido, Deposito, PresentacionCantidad, PresentacionUnidad, Ruteo, Alfa, Peso, StockMinimo, CxB, DescuentoXCaja, ImpInterno, ArMargenTeorico, CuentaContable, SubFamilia, DiasAlVto, MargenIIBB, MargenOtrosImp, ModeloEtiqueta, CantidadEtiquetas, CxP, CxPP, GeneraRemitoComponentes, Serializado) VALUES(:Codigo, :EAN, :Descripcion, :DescripcionCorta, :PrecioCosto, :PrecioVenta, :Margen, :IVA, :EsCombo, :Proveedor, :Departamento, :Marca, :Familia, :UxB, :HabilCajas, :HabilEstad, :HabilStock, :HabilOC, :HabilBalanzas, :BalDiasVto, :BalCodigo, :Tipo, :CodigoEnvase, :FechaModificacion, :FechaAlta, :HoraModificacion, :Transmitido, :Deposito, :PresentacionCantidad, :PresentacionUnidad, :Ruteo, :Alfa, :Peso, :StockMinimo, :CxB, :DescuentoXCaja, :ImpInterno, :ArMargenTeorico, :CuentaContable, :SubFamilia, :DiasAlVto, :MargenIIBB, :MargenOtrosImp, :ModeloEtiqueta, :CantidadEtiquetas, :CxP, :CxPP, :GeneraRemitoComponentes, :Serializado)")
        db.execute(sql.params(Articulos_nene=Articulos_nene))
        db.commit()
        result = db.execute(text("SELECT Codigo, EAN, Descripcion, DescripcionCorta, PrecioCosto, PrecioVenta, Margen, IVA, EsCombo, Proveedor, Departamento, Marca, Familia, UxB, HabilCajas, HabilEstad, HabilStock, HabilOC, HabilBalanzas, BalDiasVto, BalCodigo, Tipo, CodigoEnvase, FechaModificacion, FechaAlta, HoraModificacion, Transmitido, Deposito, PresentacionCantidad, PresentacionUnidad, Ruteo, Alfa, Peso, StockMinimo, CxB, DescuentoXCaja, ImpInterno, ArMargenTeorico, CuentaContable, SubFamilia, DiasAlVto, MargenIIBB, MargenOtrosImp, ModeloEtiqueta, CantidadEtiquetas, CxP, CxPP, GeneraRemitoComponentes, Serializado FROM Articulos_nene WHERE Codigo = :Codigo"), {"Codigo": Articulos_nene.Codigo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Articulos_nene")

def get(db: Session, Codigo: INTEGER):
    try:
        result = db.execute(text("SELECT Codigo, EAN, Descripcion, DescripcionCorta, PrecioCosto, PrecioVenta, Margen, IVA, EsCombo, Proveedor, Departamento, Marca, Familia, UxB, HabilCajas, HabilEstad, HabilStock, HabilOC, HabilBalanzas, BalDiasVto, BalCodigo, Tipo, CodigoEnvase, FechaModificacion, FechaAlta, HoraModificacion, Transmitido, Deposito, PresentacionCantidad, PresentacionUnidad, Ruteo, Alfa, Peso, StockMinimo, CxB, DescuentoXCaja, ImpInterno, ArMargenTeorico, CuentaContable, SubFamilia, DiasAlVto, MargenIIBB, MargenOtrosImp, ModeloEtiqueta, CantidadEtiquetas, CxP, CxPP, GeneraRemitoComponentes, Serializado FROM Articulos_nene WHERE Codigo = :Codigo"), {"Codigo": Codigo})
        Articulos_nene = result.fetchall()
        if Articulos_nene is None:
            raise HTTPException(status_code=404, detail="Articulos_nene no encontrado")
        return Articulos_nene
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Articulos_nene")
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

