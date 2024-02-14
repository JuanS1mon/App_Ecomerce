from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.marcas import MarcaCreate

# MI IDEA es tener un crud por cada tabla de la base de datos y que cada uno tenga sus funciones
# por ejemplo: crud_users.py, crud_articulos.py, crud_marcas.py, etc

#para que sirve el Session ?? https://docs.sqlalchemy.org/en/14/orm/session_api.html
def create(db: Session, descripcion: str):
    try:
        sql = text("""INSERT INTO Articulos
                   (Codigo, EAN, Descripcion, DescripcionCorta, PrecioCosto,
                   PrecioVenta, Margen, IVA, EsCombo, Proveedor,
                    Departamento, Marca, Familia, UxB, HabilCajas,
                    HabilEstad, HabilStock, HabilOC, HabilBalanzas, BalDiasVto,
                    BalCodigo, Tipo, CodigoEnvase, FechaModificacion, FechaAlta,
                    HoraModificacion, Transmitido, Deposito, PresentacionCantidad, PresentacionUnidad,
                    Ruteo, Alfa, Peso, StockMinimo, CxB, 
                   DescuentoXCaja, ImpInterno, ArMargenTeorico, CuentaContable, SubFamilia, 
                   DiasAlVto,MargenIIBB, MargenOtrosImp, ModeloEtiqueta, CantidadEtiquetas, 
                   CxP,CxPP, GeneraRemitoComponentes, Serializado, Sector)
                    VALUES(:Codigo, :EAN, :Descripcion, :DescripcionCorta, :PrecioCosto,
                    :PrecioVenta, :Margen, :IVA, :EsCombo, :Proveedor,
                    :Departamento, :Marca, :Familia, :UxB, :HabilCajas,
                    :HabilEstad, :HabilStock, :HabilOC, :HabilBalanzas, :BalDiasVto,
                    :BalCodigo, :Tipo, :CodigoEnvase, :FechaModificacion, :FechaAlta,
                    :HoraModificacion, :Transmitido, :Deposito, :PresentacionCantidad, :PresentacionUnidad,
                    :Ruteo, :Alfa, :Peso, :StockMinimo, :CxB,
                    :DescuentoXCaja, :ImpInterno, :ArMargenTeorico, :CuentaContable, :SubFamilia,
                    :DiasAlVto, :MargenIIBB, :MargenOtrosImp, :ModeloEtiqueta, :CantidadEtiquetas,
                    :CxP, :CxPP, :GeneraRemitoComponentes, :Serializado, :Sector)""")
        db.execute(sql.params(Codigo=Codigo, EAN=EAN, Descripcion=Descripcion, DescripcionCorta=DescripcionCorta, PrecioCosto=PrecioCosto,
                              PrecioVenta=PrecioVenta, Margen=Margen, IVA=IVA, EsCombo=EsCombo, Proveedor=Proveedor,
                              Departamento=Departamento, Marca=Marca, Familia=Familia, UxB=UxB, HabilCajas=HabilCajas,
                              HabilEstad=HabilEstad, HabilStock=HabilStock, HabilOC=HabilOC, HabilBalanzas=HabilBalanzas, BalDiasVto=BalDiasVto,
                              BalCodigo=BalCodigo, Tipo=Tipo, CodigoEnvase=CodigoEnvase, FechaModificacion=FechaModificacion, FechaAlta=FechaAlta,
                              HoraModificacion=HoraModificacion, Transmitido=Transmitido, Deposito=Deposito, PresentacionCantidad=PresentacionCantidad, PresentacionUnidad=PresentacionUnidad,
                              Ruteo=Ruteo, Alfa=Alfa, Peso=Peso, StockMinimo=StockMinimo, CxB=CxB,
                              DescuentoXCaja=DescuentoXCaja, ImpInterno=ImpInterno, ArMargenTeorico=ArMargenTeorico, CuentaContable=CuentaContable, SubFamilia=SubFamilia,
                              DiasAlVto=DiasAlVto, MargenIIBB=MargenIIBB, MargenOtrosImp=MargenOtrosImp, ModeloEtiqueta=ModeloEtiqueta, CantidadEtiquetas=CantidadEtiquetas,
                              CxP=CxP, CxPP=CxPP, GeneraRemitoComponentes=GeneraRemitoComponentes, Serializado=Serializado, Sector=Sector))
        db.commit()
        result = db.execute(text("SELECT codigo,descripcion FROM marcas WHERE descripcion = :descripcion"), {"descripcion": descripcion})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear la marca")




def get(db: Session, codigo: int):
    try:
        result = db.execute(text("SELECT codigo,descripcion FROM marcas WHERE codigo = :codigo"), {"codigo": codigo})
        marca = result.fetchall()
        if marca is None:
            raise HTTPException(status_code=404, detail="Marca no encontrada")
        return marca
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la marca")


def get_descripcion(db: Session, descripcion: str):
    try:
        result = db.execute(text("SELECT codigo FROM marcas WHERE descripcion = :descripcion"), {"descripcion": descripcion})
        marca = result.fetchone()
        if marca is None:
            return marca
        else:
            raise HTTPException(status_code=404, detail=f"Marca '{descripcion}',ya se encuentra registrada")
        a
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la marca")

def gets(db: Session):
    try:
        result = db.execute(text("""
    SELECT
    [Codigo],             [EAN],                [Descripcion],         [DescripcionCorta],    [PrecioCosto],
    [PrecioVenta],        [Margen],             [IVA],                 [EsCombo],             [Proveedor],
    [Departamento],       [Marca],              [Familia],             [UxB],                 [HabilCajas],
    [HabilEstad],         [HabilStock],         [HabilOC],             [HabilBalanzas],       [BalDiasVto],
    [BalCodigo],          [Tipo],               [CodigoEnvase],        [FechaModificacion],   [FechaAlta],
    [HoraModificacion],   [Transmitido],        [Deposito],            [PresentacionCantidad],[PresentacionUnidad],
    [Ruteo],             [Alfa],               [Peso],                [StockMinimo],         [CxB],
    [DescuentoXCaja],     [ImpInterno],         [ArMargenTeorico],     [CuentaContable],      [SubFamilia],
    [DiasAlVto],          [MargenIIBB],         [MargenOtrosImp],      [ModeloEtiqueta],      [CantidadEtiquetas],
    [CxP],                [CxPP],               [GeneraRemitoComponentes], [Serializado],     [Sector]
    FROM [Articulos]"""))
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
    

def delete(db: Session, codigo: int):
    try:
        statement = text("DELETE FROM Marcas WHERE codigo = :codigo")
        db.execute(statement.params(codigo=codigo))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar la marca")
    




