from pydantic import BaseModel # Importamos BaseModel de pydantic para crear modelos de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.
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
    CodigoEnvase: int
    FechaModificacion: datetime
    FechaAlta: datetime
    HoraModificacion: str
    Transmitido: bool

class ArticulosNeneCreate(Articulos):
    pass

class ArticulosNene(Articulos):
    class Config:
        from_attributes = True


    