from pydantic import BaseModel
from datetime import datetime

class Articulos(BaseModel):
    Codigo: int
    EAN: float
    Descripcion: str
    DescripcionCorta: str
    PrecioCosto: float
    PrecioVenta: float
    Margen: float
    IVA: int
    EsCombo: bool
    Proveedor: int
    Departamento: int
    Marca: int
    Familia: int
    UxB: int
    HabilCajas: bool
    HabilEstad: bool
    HabilStock: bool
    HabilOC: bool
    HabilBalanzas: bool
    BalDiasVto: int
    BalCodigo: int
    Tipo: str
    CodigoEnvase: float
    FechaModificacion: datetime
    FechaAlta: datetime
    HoraModificacion: str
    Transmitido: bool
    Deposito: int
    PresentacionCantidad: float
    PresentacionUnidad: str
    Ruteo: str
    Alfa: str
    Peso: float
    StockMinimo: float
    CxB: int
    DescuentoXCaja: float
    ImpInterno: float
    ArMargenTeorico: float
    CuentaContable: float
    SubFamilia: int
    DiasAlVto: int
    MargenIIBB: float
    MargenOtrosImp: float
    ModeloEtiqueta: str
    CantidadEtiquetas: int
    CxP: int
    CxPP: int
    GeneraRemitoComponentes: bool
    Serializado: bool
    Sector: int

class ArticulosNeneCreate(Articulos):
    pass

class ArticulosNene(Articulos):
    class Config:
        from_attributes = True


