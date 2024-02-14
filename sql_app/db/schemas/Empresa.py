
from pydantic import BaseModel
from datetime import datetime

class EmpresasModel(BaseModel):
    Numero: int
    Nombre: str
    CUIT: str
    EjercicioActual: int
    FechaCierreCaja: datetime
    Logo: str
    RazonSocial: str
    Direccion: str
    NroAgRet: str
    OrdenPago: int
    R_IIBB: int
    R_gan: int
    OPCant: int
    RetCant: int
    FechaCierreIva: datetime
    FechaProximoCierreIva: datetime
    TipoOrdenPago: int
    Color: int
    FormatoRecibo: int
    FechaCierreBancos: datetime
    PathOP: str
    PathRET: str
    Localidad: int
    PathLogoOP: str
    AFIP_URLTFA: str
    AFIP_URLPFX: str
    PuntoVentaComision: int
    PuertoImpresionDP: str
    NroAgRetAGIP: str
    NroAgRetIIBB: str
    NroAgRetAPR: str
    BancoDefecto: int
