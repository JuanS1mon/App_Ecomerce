# Imports de bibliotecas estándar
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union

# Imports de terceros
from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator

# Enums para los schemas (réplicas de los enums del modelo)
class TipoComprobanteEnum(str, Enum):
    FACTURA_A = "A"
    FACTURA_B = "B"
    FACTURA_C = "C"
    NOTA_CREDITO_A = "NCA"
    NOTA_CREDITO_B = "NCB"
    NOTA_CREDITO_C = "NCC"
    NOTA_DEBITO_A = "NDA"
    NOTA_DEBITO_B = "NDB"
    NOTA_DEBITO_C = "NDC"

class EstadoComprobanteEnum(str, Enum):
    BORRADOR = "BORRADOR"
    PENDIENTE = "PENDIENTE" 
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ANULADO = "ANULADO"

class TipoDocumentoEnum(str, Enum):
    CUIT = "CUIT"
    CUIL = "CUIL"
    DNI = "DNI"
    PASAPORTE = "PASAPORTE"
    OTRO = "OTRO"

class CondicionIVAEnum(str, Enum):
    RESPONSABLE_INSCRIPTO = "RESPONSABLE_INSCRIPTO"
    MONOTRIBUTISTA = "MONOTRIBUTISTA"
    EXENTO = "EXENTO"
    CONSUMIDOR_FINAL = "CONSUMIDOR_FINAL"
    NO_CATEGORIZADO = "NO_CATEGORIZADO"

class MedioPagoEnum(str, Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA_CREDITO = "TARJETA_CREDITO"
    TARJETA_DEBITO = "TARJETA_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CHEQUE = "CHEQUE"
    OTRO = "OTRO"

# Schemas de Cliente
class ClienteBase(BaseModel):
    razon_social: str
    nombre_fantasia: Optional[str] = None
    tipo_documento: TipoDocumentoEnum
    numero_documento: str
    condicion_iva: CondicionIVAEnum
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_fantasia: Optional[str] = None
    tipo_documento: Optional[TipoDocumentoEnum] = None
    numero_documento: Optional[str] = None
    condicion_iva: Optional[CondicionIVAEnum] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None

class ClienteRead(ClienteBase):
    id: int
    fecha_alta: datetime
    activo: bool
    model_config = ConfigDict(from_attributes=True)

# Schemas de Punto de Venta
class PuntoVentaBase(BaseModel):
    numero: int
    descripcion: Optional[str] = None
    direccion: Optional[str] = None

class PuntoVentaCreate(PuntoVentaBase):
    pass

class PuntoVentaUpdate(BaseModel):
    numero: Optional[int] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

class PuntoVentaRead(PuntoVentaBase):
    id: int
    activo: bool
    model_config = ConfigDict(from_attributes=True)

# Schemas de Item Factura
class ItemFacturaBase(BaseModel):
    descripcion: str
    cantidad: float
    precio_unitario: float
    porcentaje_iva: float
    codigo_producto: Optional[str] = None

class ItemFacturaCreate(ItemFacturaBase):
    pass

class ItemFacturaUpdate(BaseModel):
    descripcion: Optional[str] = None
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    porcentaje_iva: Optional[float] = None
    codigo_producto: Optional[str] = None

class ItemFacturaRead(ItemFacturaBase):
    id: int
    subtotal: float
    importe_iva: float
    total: float
    factura_id: int
    model_config = ConfigDict(from_attributes=True)

# Schemas de Factura
class FacturaBase(BaseModel):
    tipo_comprobante: TipoComprobanteEnum
    punto_venta_id: int
    numero: int
    fecha_emision: datetime
    cliente_id: int
    observaciones: Optional[str] = None
    medio_pago: MedioPagoEnum = MedioPagoEnum.EFECTIVO
    fecha_vencimiento_pago: Optional[datetime] = None

class FacturaCreate(FacturaBase):
    items: List[ItemFacturaCreate]

class FacturaUpdate(BaseModel):
    tipo_comprobante: Optional[TipoComprobanteEnum] = None
    punto_venta_id: Optional[int] = None
    numero: Optional[int] = None
    fecha_emision: Optional[datetime] = None
    cliente_id: Optional[int] = None
    observaciones: Optional[str] = None
    estado: Optional[EstadoComprobanteEnum] = None
    medio_pago: Optional[MedioPagoEnum] = None
    fecha_vencimiento_pago: Optional[datetime] = None
    items: Optional[List[Union[ItemFacturaCreate, ItemFacturaUpdate]]] = None

class FacturaRead(FacturaBase):
    id: int
    subtotal: float
    iva: float
    otros_impuestos: float
    total: float
    cae: Optional[str] = None
    vencimiento_cae: Optional[datetime] = None
    estado: EstadoComprobanteEnum
    creado_por: Optional[str] = None
    fecha_creacion: datetime
    modificado_por: Optional[str] = None
    fecha_modificacion: Optional[datetime] = None
    pdf_generado: bool
    ruta_pdf: Optional[str] = None
    items: List[ItemFacturaRead] = []
    
    model_config = ConfigDict(from_attributes=True)

# Aliases para compatibilidad con nombres de clases antiguos
FacturacionCreate = FacturaCreate
FacturacionUpdate = FacturaUpdate
FacturacionRead = FacturaRead

# Schema para los eventos de factura
class EventoFacturaBase(BaseModel):
    factura_id: int
    tipo_evento: str
    descripcion: Optional[str] = None
    usuario: Optional[str] = None

class EventoFacturaCreate(EventoFacturaBase):
    pass

class EventoFacturaRead(EventoFacturaBase):
    id: int
    fecha: datetime
    model_config = ConfigDict(from_attributes=True)

# Schema para la configuración de facturación
class ConfiguracionFacturacionBase(BaseModel):
    razon_social: str
    nombre_fantasia: Optional[str] = None
    cuit: str
    ingresos_brutos: Optional[str] = None
    inicio_actividades: Optional[datetime] = None
    condicion_iva: CondicionIVAEnum
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_path: Optional[str] = None
    certificado_path: Optional[str] = None
    clave_path: Optional[str] = None
    ws_wsdl: Optional[str] = None
    homo: bool = True

class ConfiguracionFacturacionCreate(ConfiguracionFacturacionBase):
    pass

class ConfiguracionFacturacionUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_fantasia: Optional[str] = None
    cuit: Optional[str] = None
    ingresos_brutos: Optional[str] = None
    inicio_actividades: Optional[datetime] = None
    condicion_iva: Optional[CondicionIVAEnum] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_path: Optional[str] = None
    certificado_path: Optional[str] = None
    clave_path: Optional[str] = None
    ws_wsdl: Optional[str] = None
    homo: Optional[bool] = None

class ConfiguracionFacturacionRead(ConfiguracionFacturacionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Schemas para búsquedas avanzadas
class FacturaBusquedaParams(BaseModel):
    cliente_id: Optional[int] = None
    tipo_comprobante: Optional[TipoComprobanteEnum] = None
    estado: Optional[EstadoComprobanteEnum] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    numero: Optional[int] = None
    punto_venta_id: Optional[int] = None
    documento_cliente: Optional[str] = None
    razon_social_cliente: Optional[str] = None
    importe_desde: Optional[float] = None
    importe_hasta: Optional[float] = None
    con_cae: Optional[bool] = None
    con_pdf: Optional[bool] = None
    medio_pago: Optional[MedioPagoEnum] = None
    page: int = 1
    limit: int = 20
    order_by: str = "fecha_emision"
    order_dir: str = "desc"

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
