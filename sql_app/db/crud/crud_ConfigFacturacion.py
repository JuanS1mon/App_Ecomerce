from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.ConfigFacturacion import ConfigfacturacionCreate

def create(db: Session, ConfigFacturacion: ConfigfacturacionCreate):
    try:
        sql = text("INSERT INTO ConfigFacturacion(Sucursal, PuntoVenta, PuertoFactura, ItemsFactura, ProximaFacturaA, ProximaFacturaB, ProximoRemito, LineasImpresion, MonedaContado, MonedaCtaCte, ConceptoIngreso, ConceptoEgreso, MonedaFacturacionDefecto, ProximaNCA, ProximaNCB, Empresa, Imprime, ClienteFacturacionDefecto, MonedaFacturacioDefecto, FormularioUnico, FormularioUnicoND, ProximaNotaDebitoA, ProximaNotaDebitoB, ProximaNotaDebitoE, ModeloCbte, CopiasComprobante, ProximaNotaCreditoA, PuertoImpresion, EsFacturaElectronica, ComprobantesCant, MarcaFiscal, ModeloFiscal, ProximaNotaCreditoB, ProximaFacturaE, MonedaDefecto, ModificarNroComprobante, ImporteMaximo, ModoFacturacion, FacturaUnidadDefecto, ProximaNotaCreditoE, CobranzaEnComprobante, PathPDF, FCSaltoConArrastre, Descripcion, ExcluyeEnHojaRuta, CantCopiasRemito, ImporteMaxFC, AplicaPercepciones, CentroCosto, SucursalRemito, FC_RemitoEgresoCombo, SucursalEgresoCombo, ConceptoEgresoCombo, CantLineasControl, FCEmiteRemitoEgreso, EsPreDP, UsaIvaDepartamento, EsFacturaCreditoElectronica) VALUES(:Sucursal, :PuntoVenta, :PuertoFactura, :ItemsFactura, :ProximaFacturaA, :ProximaFacturaB, :ProximoRemito, :LineasImpresion, :MonedaContado, :MonedaCtaCte, :ConceptoIngreso, :ConceptoEgreso, :MonedaFacturacionDefecto, :ProximaNCA, :ProximaNCB, :Empresa, :Imprime, :ClienteFacturacionDefecto, :MonedaFacturacioDefecto, :FormularioUnico, :FormularioUnicoND, :ProximaNotaDebitoA, :ProximaNotaDebitoB, :ProximaNotaDebitoE, :ModeloCbte, :CopiasComprobante, :ProximaNotaCreditoA, :PuertoImpresion, :EsFacturaElectronica, :ComprobantesCant, :MarcaFiscal, :ModeloFiscal, :ProximaNotaCreditoB, :ProximaFacturaE, :MonedaDefecto, :ModificarNroComprobante, :ImporteMaximo, :ModoFacturacion, :FacturaUnidadDefecto, :ProximaNotaCreditoE, :CobranzaEnComprobante, :PathPDF, :FCSaltoConArrastre, :Descripcion, :ExcluyeEnHojaRuta, :CantCopiasRemito, :ImporteMaxFC, :AplicaPercepciones, :CentroCosto, :SucursalRemito, :FC_RemitoEgresoCombo, :SucursalEgresoCombo, :ConceptoEgresoCombo, :CantLineasControl, :FCEmiteRemitoEgreso, :EsPreDP, :UsaIvaDepartamento, :EsFacturaCreditoElectronica)")
        db.execute(sql.params(ConfigFacturacion=ConfigFacturacion))
        db.commit()
        result = db.execute(text("SELECT Sucursal, PuntoVenta, PuertoFactura, ItemsFactura, ProximaFacturaA, ProximaFacturaB, ProximoRemito, LineasImpresion, MonedaContado, MonedaCtaCte, ConceptoIngreso, ConceptoEgreso, MonedaFacturacionDefecto, ProximaNCA, ProximaNCB, Empresa, Imprime, ClienteFacturacionDefecto, MonedaFacturacioDefecto, FormularioUnico, FormularioUnicoND, ProximaNotaDebitoA, ProximaNotaDebitoB, ProximaNotaDebitoE, ModeloCbte, CopiasComprobante, ProximaNotaCreditoA, PuertoImpresion, EsFacturaElectronica, ComprobantesCant, MarcaFiscal, ModeloFiscal, ProximaNotaCreditoB, ProximaFacturaE, MonedaDefecto, ModificarNroComprobante, ImporteMaximo, ModoFacturacion, FacturaUnidadDefecto, ProximaNotaCreditoE, CobranzaEnComprobante, PathPDF, FCSaltoConArrastre, Descripcion, ExcluyeEnHojaRuta, CantCopiasRemito, ImporteMaxFC, AplicaPercepciones, CentroCosto, SucursalRemito, FC_RemitoEgresoCombo, SucursalEgresoCombo, ConceptoEgresoCombo, CantLineasControl, FCEmiteRemitoEgreso, EsPreDP, UsaIvaDepartamento, EsFacturaCreditoElectronica FROM ConfigFacturacion WHERE Sucursal = :Sucursal"), {"Sucursal": ConfigFacturacion.Sucursal})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el ConfigFacturacion")

def get(db: Session, Sucursal: INTEGER):
    try:
        result = db.execute(text("SELECT Sucursal, PuntoVenta, PuertoFactura, ItemsFactura, ProximaFacturaA, ProximaFacturaB, ProximoRemito, LineasImpresion, MonedaContado, MonedaCtaCte, ConceptoIngreso, ConceptoEgreso, MonedaFacturacionDefecto, ProximaNCA, ProximaNCB, Empresa, Imprime, ClienteFacturacionDefecto, MonedaFacturacioDefecto, FormularioUnico, FormularioUnicoND, ProximaNotaDebitoA, ProximaNotaDebitoB, ProximaNotaDebitoE, ModeloCbte, CopiasComprobante, ProximaNotaCreditoA, PuertoImpresion, EsFacturaElectronica, ComprobantesCant, MarcaFiscal, ModeloFiscal, ProximaNotaCreditoB, ProximaFacturaE, MonedaDefecto, ModificarNroComprobante, ImporteMaximo, ModoFacturacion, FacturaUnidadDefecto, ProximaNotaCreditoE, CobranzaEnComprobante, PathPDF, FCSaltoConArrastre, Descripcion, ExcluyeEnHojaRuta, CantCopiasRemito, ImporteMaxFC, AplicaPercepciones, CentroCosto, SucursalRemito, FC_RemitoEgresoCombo, SucursalEgresoCombo, ConceptoEgresoCombo, CantLineasControl, FCEmiteRemitoEgreso, EsPreDP, UsaIvaDepartamento, EsFacturaCreditoElectronica FROM ConfigFacturacion WHERE Sucursal = :Sucursal"), {"Sucursal": Sucursal})
        ConfigFacturacion = result.fetchall()
        if ConfigFacturacion is None:
            raise HTTPException(status_code=404, detail="Configfacturacion no encontrado")
        return ConfigFacturacion
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el ConfigFacturacion")
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

