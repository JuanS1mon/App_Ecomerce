from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Configfacturacion(Base):
    __tablename__ = 'ConfigFacturacion'
    Sucursal = Column(Integer, primary_key=True)
    PuntoVenta = Column(Integer, primary_key=True)
    PuertoFactura = Column(String(50))
    ItemsFactura = Column(Integer, primary_key=True)
    ProximaFacturaA = Column(Integer, primary_key=True)
    ProximaFacturaB = Column(Integer, primary_key=True)
    ProximoRemito = Column(Integer, primary_key=True)
    LineasImpresion = Column(Integer, primary_key=True)
    MonedaContado = Column(Integer, primary_key=True)
    MonedaCtaCte = Column(Integer, primary_key=True)
    ConceptoIngreso = Column(Integer, primary_key=True)
    ConceptoEgreso = Column(Integer, primary_key=True)
    MonedaFacturacionDefecto = Column(Integer, primary_key=True)
    ProximaNCA = Column(Integer, primary_key=True)
    ProximaNCB = Column(Integer, primary_key=True)
    Empresa = Column(Integer, primary_key=True)
    Imprime = Column(String(50))
    ClienteFacturacionDefecto = Column(Integer, primary_key=True)
    MonedaFacturacioDefecto = Column(Integer, primary_key=True)
    ProximaNotaDebitoA = Column(Integer, primary_key=True)
    ProximaNotaDebitoB = Column(Integer, primary_key=True)
    ProximaNotaDebitoE = Column(Integer, primary_key=True)
    ModeloCbte = Column(Integer, primary_key=True)
    CopiasComprobante = Column(Integer, primary_key=True)
    ProximaNotaCreditoA = Column(Integer, primary_key=True)
    PuertoImpresion = Column(String(50))
    ComprobantesCant = Column(Integer, primary_key=True)
    MarcaFiscal = Column(String(50))
    ModeloFiscal = Column(String(50))
    ProximaNotaCreditoB = Column(Integer, primary_key=True)
    ProximaFacturaE = Column(Integer, primary_key=True)
    MonedaDefecto = Column(Integer, primary_key=True)
    ModoFacturacion = Column(Integer, primary_key=True)
    ProximaNotaCreditoE = Column(Integer, primary_key=True)
    PathPDF = Column(String(50))
    Descripcion = Column(String(50))
    CantCopiasRemito = Column(Integer, primary_key=True)
    CentroCosto = Column(Integer, primary_key=True)
    SucursalRemito = Column(Integer, primary_key=True)
    SucursalEgresoCombo = Column(Integer, primary_key=True)
    ConceptoEgresoCombo = Column(Integer, primary_key=True)
    CantLineasControl = Column(Integer, primary_key=True)

from pydantic import BaseModel

class ConfigfacturacionModel(BaseModel):
    Sucursal: int
    PuntoVenta: int
    PuertoFactura: str
    ItemsFactura: int
    ProximaFacturaA: int
    ProximaFacturaB: int
    ProximoRemito: int
    LineasImpresion: int
    MonedaContado: int
    MonedaCtaCte: int
    ConceptoIngreso: int
    ConceptoEgreso: int
    MonedaFacturacionDefecto: int
    ProximaNCA: int
    ProximaNCB: int
    Empresa: int
    Imprime: str
    ClienteFacturacionDefecto: int
    MonedaFacturacioDefecto: int
    ProximaNotaDebitoA: int
    ProximaNotaDebitoB: int
    ProximaNotaDebitoE: int
    ModeloCbte: int
    CopiasComprobante: int
    ProximaNotaCreditoA: int
    PuertoImpresion: str
    ComprobantesCant: int
    MarcaFiscal: str
    ModeloFiscal: str
    ProximaNotaCreditoB: int
    ProximaFacturaE: int
    MonedaDefecto: int
    ModoFacturacion: int
    ProximaNotaCreditoE: int
    PathPDF: str
    Descripcion: str
    CantCopiasRemito: int
    CentroCosto: int
    SucursalRemito: int
    SucursalEgresoCombo: int
    ConceptoEgresoCombo: int
    CantLineasControl: int
