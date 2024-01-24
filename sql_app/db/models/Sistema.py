from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sistema(Base):
    __tablename__ = 'Sistema'
    Sucursal = Column(Integer, primary_key=True)
    Modo = Column(String(50))
    PuertoReporteCaja = Column(String(50))
    LargoDescripcion = Column(Integer, primary_key=True)
    ProximoRemitoIngreso = Column(Integer, primary_key=True)
    ProximoRemitoEgreso = Column(Integer, primary_key=True)
    PathRecoleccion = Column(String(50))
    PuertoOC = Column(String(50))
    LineasImpresionOC = Column(Integer, primary_key=True)
    ImprimirRemito = Column(String(50))
    PuertoRemito = Column(String(50))
    PuertoPDT = Column(Integer, primary_key=True)
    TipoMovimientoDeposito = Column(Integer, primary_key=True)
    TipoMovimientoPagoProveedor = Column(Integer, primary_key=True)
    TipoMovimientoCompra = Column(Integer, primary_key=True)
    TipoMovimientoEmisionCheque = Column(Integer, primary_key=True)
    TipoMovimientoIngresoCh3ro = Column(Integer, primary_key=True)
    TipoMovimientoVentaContado = Column(Integer, primary_key=True)
    TipoMovimientoVentaCtaCte = Column(Integer, primary_key=True)
    TipoMovimientoCobroCtaCte = Column(Integer, primary_key=True)
    TipoLibroIVACompras = Column(Integer, primary_key=True)
    PuertoReporteProveedores = Column(String(50))
    PuertoImpresionBancos = Column(String(50))
    SucursalPrecio2 = Column(Integer, primary_key=True)
    PuertoImpresionIVAVentas = Column(String(50))
    TipoMovRendicionCajero = Column(Integer, primary_key=True)
    VerRemitoPor = Column(String(50))
    PathRemitos = Column(String(50))
    ConceptoRecepcionEnvio = Column(Integer, primary_key=True)
    UoBOrdenCompra = Column(String(50))
    PuertoReposicionPrecarga = Column(String(50))
    ModeloColector = Column(String(50))
    FormatoClienFC = Column(Integer, primary_key=True)
    TipoReporteIvaVentas = Column(Integer, primary_key=True)
    RemitoCargaTipoCosto = Column(String(50))
    TipoMovimientoEgresoCh3ro = Column(Integer, primary_key=True)
    TablaCardex = Column(String(50))
    OrdenCompraConfiguracion = Column(Integer, primary_key=True)
    RemitoCargaModificaArticulo = Column(String(50))
    FormatoRemito = Column(Integer, primary_key=True)
    PathGeneracionColectora = Column(String(50))
    TipoMovimientoIngresoTicket = Column(Integer, primary_key=True)
    TipoReporteNovedades = Column(Integer, primary_key=True)
    PuertoImpresionIvaCompras = Column(String(50))
    CambioPrecioCantBonif = Column(Integer, primary_key=True)
    EmpresaDefecto = Column(Integer, primary_key=True)
    CargaRemitoUoB = Column(String(50))
    TipoCredito = Column(String(50))
    PlanCreditoComprasPOS = Column(Integer, primary_key=True)
    PlanCreditoGastosAdmin = Column(Integer, primary_key=True)
    PuertoInventario = Column(String(50))
    PathPresupuesto = Column(String(50))
    TipoMovimientoCobroCredito = Column(Integer, primary_key=True)
    BonifFechasActualiza = Column(String(50))
    ClienteDefecto = Column(Integer, primary_key=True)
    VendedorDefecto = Column(Integer, primary_key=True)
    PuntoVentaDefecto = Column(Integer, primary_key=True)
    ArtListasModo = Column(String(50))
    PuertoPlanillaCarga = Column(String(50))
    FormatoImpresionOrdenCompra = Column(Integer, primary_key=True)
    PuntosXPeso = Column(Integer, primary_key=True)
    PathImagenesScoring = Column(String(50))
    TipoReporteCosto = Column(Integer, primary_key=True)
    ImpuestoRIIBB = Column(Integer, primary_key=True)
    ImpuestoRGAN = Column(Integer, primary_key=True)
    ConceptoEgresoCombo = Column(Integer, primary_key=True)
    GuardarTK = Column(Integer, primary_key=True)
    TipoMovimientoVenta = Column(Integer, primary_key=True)
    ClienteWeb = Column(Integer, primary_key=True)
    FormatoInventario = Column(Integer, primary_key=True)
    TipoBonificacionFecha = Column(String(50))
    MonedaComprasContado = Column(Integer, primary_key=True)
    FormatoImpresionOrdenCompras = Column(Integer, primary_key=True)
    TipoReporteChequesTerceros = Column(Integer, primary_key=True)
    PathPDFRecibos = Column(String(50))
    TipoMovimientoCierre = Column(Integer, primary_key=True)
    TipoMovimientoApertura = Column(Integer, primary_key=True)
    TipoMovimientoRefundicion = Column(Integer, primary_key=True)
    ConceptoEgresoDP = Column(Integer, primary_key=True)
    ConceptoIngresoCompra = Column(Integer, primary_key=True)
    CantidadDecimalesPrecioVenta = Column(Integer, primary_key=True)
    ConceptoEgresoCreditoCompra = Column(Integer, primary_key=True)
    SucursalEgresoCombo = Column(Integer, primary_key=True)
    PuertoImpresionClientes = Column(String(50))
    TipoMovimientoTransferenciaCtaCte = Column(Integer, primary_key=True)
    PathImagenesArticulos = Column(String(50))
    PagoDefecto = Column(Integer, primary_key=True)
    CantidadDecimalesImpresionComprobantes = Column(Integer, primary_key=True)
    TipoListaPrecio = Column(Integer, primary_key=True)
    ModoOfertas = Column(Integer, primary_key=True)
    ModeloEtiquetaDef = Column(String(50))
    ModeloEtiquetaDefOfertas = Column(String(50))
    ModeloEtiquetaDefPromociones = Column(String(50))
    CambioCostoComboActualiza = Column(String(50))
    PathOCPDF = Column(String(50))
    LecturaQTK = Column(String(50))
    TipoFacturacion = Column(String(50))
    ImpuestoRAPR = Column(Integer, primary_key=True)
    TipoPercepcion2 = Column(Integer, primary_key=True)
    PvCreditos = Column(Integer, primary_key=True)
    OCBonificacionUnidadesPosicion = Column(Integer, primary_key=True)
    BloqueoPorOCSinFinalizarCant = Column(Integer, primary_key=True)
    DiasBloqueoPagoPreDP = Column(Integer, primary_key=True)
    ConceptoRemCancelaPreDP = Column(Integer, primary_key=True)
    ArtRangoDesde = Column(Integer, primary_key=True)
    ArtRangoHasta = Column(Integer, primary_key=True)
    PuertoImpresionRecibos = Column(String(50))
    ModificacionesCargaTipoCosto = Column(String(50))
    RemitoElaboradosConceptoEgreso = Column(Integer, primary_key=True)
    RemitoElaboradosConceptoIngreso = Column(Integer, primary_key=True)
    RemitoElaboradosProveedor = Column(Integer, primary_key=True)
    ProduccionConceptoFinalizados = Column(Integer, primary_key=True)
    ProduccionConceptoIngredientes = Column(Integer, primary_key=True)
    ProduccionProveedorFinalizados = Column(Integer, primary_key=True)
    ProduccionProveedorIngredientes = Column(Integer, primary_key=True)
    SucursalProduccionElaborados = Column(Integer, primary_key=True)
    PathImgCbtesProve = Column(String(50))
    PathImgCbtesProveOrigen = Column(String(50))
    ModeloEtiquetaDefPromosDetPorc = Column(String(50))
    ModeloEtiquetaDefPromosDetCant = Column(String(50))
    MinutosUmbralHorasExtras = Column(Integer, primary_key=True)
    IngresoAMDefecto = Column(DateTime)
    IngresoPMDefecto = Column(DateTime)
    CantDiasPrevActVentas = Column(Integer, primary_key=True)

from pydantic import BaseModel

class SistemaModel(BaseModel):
    Sucursal: int
    Modo: str
    PuertoReporteCaja: str
    LargoDescripcion: int
    ProximoRemitoIngreso: int
    ProximoRemitoEgreso: int
    PathRecoleccion: str
    PuertoOC: str
    LineasImpresionOC: int
    ImprimirRemito: str
    PuertoRemito: str
    PuertoPDT: int
    TipoMovimientoDeposito: int
    TipoMovimientoPagoProveedor: int
    TipoMovimientoCompra: int
    TipoMovimientoEmisionCheque: int
    TipoMovimientoIngresoCh3ro: int
    TipoMovimientoVentaContado: int
    TipoMovimientoVentaCtaCte: int
    TipoMovimientoCobroCtaCte: int
    TipoLibroIVACompras: int
    PuertoReporteProveedores: str
    PuertoImpresionBancos: str
    SucursalPrecio2: int
    PuertoImpresionIVAVentas: str
    TipoMovRendicionCajero: int
    VerRemitoPor: str
    PathRemitos: str
    ConceptoRecepcionEnvio: int
    UoBOrdenCompra: str
    PuertoReposicionPrecarga: str
    ModeloColector: str
    FormatoClienFC: int
    TipoReporteIvaVentas: int
    RemitoCargaTipoCosto: str
    TipoMovimientoEgresoCh3ro: int
    TablaCardex: str
    OrdenCompraConfiguracion: int
    RemitoCargaModificaArticulo: str
    FormatoRemito: int
    PathGeneracionColectora: str
    TipoMovimientoIngresoTicket: int
    TipoReporteNovedades: int
    PuertoImpresionIvaCompras: str
    CambioPrecioCantBonif: int
    EmpresaDefecto: int
    CargaRemitoUoB: str
    TipoCredito: str
    PlanCreditoComprasPOS: int
    PlanCreditoGastosAdmin: int
    PuertoInventario: str
    PathPresupuesto: str
    TipoMovimientoCobroCredito: int
    BonifFechasActualiza: str
    ClienteDefecto: int
    VendedorDefecto: int
    PuntoVentaDefecto: int
    ArtListasModo: str
    PuertoPlanillaCarga: str
    FormatoImpresionOrdenCompra: int
    PuntosXPeso: int
    PathImagenesScoring: str
    TipoReporteCosto: int
    ImpuestoRIIBB: int
    ImpuestoRGAN: int
    ConceptoEgresoCombo: int
    GuardarTK: int
    TipoMovimientoVenta: int
    ClienteWeb: int
    FormatoInventario: int
    TipoBonificacionFecha: str
    MonedaComprasContado: int
    FormatoImpresionOrdenCompras: int
    TipoReporteChequesTerceros: int
    PathPDFRecibos: str
    TipoMovimientoCierre: int
    TipoMovimientoApertura: int
    TipoMovimientoRefundicion: int
    ConceptoEgresoDP: int
    ConceptoIngresoCompra: int
    CantidadDecimalesPrecioVenta: int
    ConceptoEgresoCreditoCompra: int
    SucursalEgresoCombo: int
    PuertoImpresionClientes: str
    TipoMovimientoTransferenciaCtaCte: int
    PathImagenesArticulos: str
    PagoDefecto: int
    CantidadDecimalesImpresionComprobantes: int
    TipoListaPrecio: int
    ModoOfertas: int
    ModeloEtiquetaDef: str
    ModeloEtiquetaDefOfertas: str
    ModeloEtiquetaDefPromociones: str
    CambioCostoComboActualiza: str
    PathOCPDF: str
    LecturaQTK: str
    TipoFacturacion: str
    ImpuestoRAPR: int
    TipoPercepcion2: int
    PvCreditos: int
    OCBonificacionUnidadesPosicion: int
    BloqueoPorOCSinFinalizarCant: int
    DiasBloqueoPagoPreDP: int
    ConceptoRemCancelaPreDP: int
    ArtRangoDesde: int
    ArtRangoHasta: int
    PuertoImpresionRecibos: str
    ModificacionesCargaTipoCosto: str
    RemitoElaboradosConceptoEgreso: int
    RemitoElaboradosConceptoIngreso: int
    RemitoElaboradosProveedor: int
    ProduccionConceptoFinalizados: int
    ProduccionConceptoIngredientes: int
    ProduccionProveedorFinalizados: int
    ProduccionProveedorIngredientes: int
    SucursalProduccionElaborados: int
    PathImgCbtesProve: str
    PathImgCbtesProveOrigen: str
    ModeloEtiquetaDefPromosDetPorc: str
    ModeloEtiquetaDefPromosDetCant: str
    MinutosUmbralHorasExtras: int
    IngresoAMDefecto: datetime
    IngresoPMDefecto: datetime
    CantDiasPrevActVentas: int
