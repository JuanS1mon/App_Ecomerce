from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from sql_app.db.database import Base

# Enums para los tipos de datos específicos
class TipoComprobante(enum.Enum):
    FACTURA_A = "A"
    FACTURA_B = "B"
    FACTURA_C = "C"
    NOTA_CREDITO_A = "NCA"
    NOTA_CREDITO_B = "NCB"
    NOTA_CREDITO_C = "NCC"
    NOTA_DEBITO_A = "NDA"
    NOTA_DEBITO_B = "NDB"
    NOTA_DEBITO_C = "NDC"

class EstadoComprobante(enum.Enum):
    BORRADOR = "BORRADOR"
    PENDIENTE = "PENDIENTE" 
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ANULADO = "ANULADO"

class TipoDocumento(enum.Enum):
    CUIT = "CUIT"
    CUIL = "CUIL"
    DNI = "DNI"
    PASAPORTE = "PASAPORTE"
    OTRO = "OTRO"

class CondicionIVA(enum.Enum):
    RESPONSABLE_INSCRIPTO = "RESPONSABLE_INSCRIPTO"
    MONOTRIBUTISTA = "MONOTRIBUTISTA"
    EXENTO = "EXENTO"
    CONSUMIDOR_FINAL = "CONSUMIDOR_FINAL"
    NO_CATEGORIZADO = "NO_CATEGORIZADO"

class MedioPago(enum.Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA_CREDITO = "TARJETA_CREDITO"
    TARJETA_DEBITO = "TARJETA_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CHEQUE = "CHEQUE"
    OTRO = "OTRO"

# Modelo para el cliente
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(100), nullable=False)
    nombre_fantasia = Column(String(100))
    tipo_documento = Column(Enum(TipoDocumento), nullable=False)
    numero_documento = Column(String(20), nullable=False, unique=True, index=True)
    condicion_iva = Column(Enum(CondicionIVA), nullable=False)
    direccion = Column(String(200))
    localidad = Column(String(100))
    provincia = Column(String(100))
    codigo_postal = Column(String(10))
    telefono = Column(String(20))
    email = Column(String(100))
    fecha_alta = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    facturas = relationship("Factura", back_populates="cliente")
    
    def __repr__(self):
        return f"Cliente(id={self.id}, razon_social={self.razon_social}, documento={self.tipo_documento.value}-{self.numero_documento})"

# Modelo para el punto de venta
class PuntoVenta(Base):
    __tablename__ = "puntos_venta"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, nullable=False, unique=True)
    descripcion = Column(String(100))
    direccion = Column(String(200))
    activo = Column(Boolean, default=True)
    
    # Relaciones
    facturas = relationship("Factura", back_populates="punto_venta")
    
    def __repr__(self):
        return f"PuntoVenta(id={self.id}, numero={self.numero})"

# Modelo para la factura
class Factura(Base):
    __tablename__ = "facturas"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_comprobante = Column(Enum(TipoComprobante), nullable=False)
    punto_venta_id = Column(Integer, ForeignKey("puntos_venta.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    fecha_emision = Column(DateTime, nullable=False, default=datetime.now)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    subtotal = Column(Float, nullable=False)
    iva = Column(Float, nullable=False)
    otros_impuestos = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    cae = Column(String(20))
    vencimiento_cae = Column(DateTime)
    observaciones = Column(Text)
    estado = Column(Enum(EstadoComprobante), default=EstadoComprobante.BORRADOR)
    medio_pago = Column(Enum(MedioPago), default=MedioPago.EFECTIVO)
    fecha_vencimiento_pago = Column(DateTime)
    creado_por = Column(String(100))
    fecha_creacion = Column(DateTime, default=datetime.now)
    modificado_por = Column(String(100))
    fecha_modificacion = Column(DateTime, onupdate=datetime.now)
    pdf_generado = Column(Boolean, default=False)
    ruta_pdf = Column(String(255))
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="facturas")
    punto_venta = relationship("PuntoVenta", back_populates="facturas")
    items = relationship("ItemFactura", back_populates="factura", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Factura(id={self.id}, tipo={self.tipo_comprobante.value}, punto_venta={self.punto_venta.numero}, numero={self.numero}, total={self.total})"

# Modelo para los items de la factura
class ItemFactura(Base):
    __tablename__ = "items_factura"
    
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    descripcion = Column(String(200), nullable=False)
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    porcentaje_iva = Column(Float, nullable=False)  # 21%, 10.5%, etc.
    subtotal = Column(Float, nullable=False)  # cantidad * precio_unitario
    importe_iva = Column(Float, nullable=False)  # subtotal * (porcentaje_iva/100)
    total = Column(Float, nullable=False)  # subtotal + importe_iva
    codigo_producto = Column(String(50))  # Opcional, para referencia
    
    # Relaciones
    factura = relationship("Factura", back_populates="items")
    
    def __repr__(self):
        return f"ItemFactura(id={self.id}, descripcion={self.descripcion}, cantidad={self.cantidad}, total={self.total})"

# Modelo para el registro de eventos de la factura
class EventoFactura(Base):
    __tablename__ = "eventos_factura"
    
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    descripcion = Column(Text)
    usuario = Column(String(100))
    fecha = Column(DateTime, default=datetime.now)
    
    # Relaciones
    factura = relationship("Factura")
    
    def __repr__(self):
        return f"EventoFactura(id={self.id}, factura_id={self.factura_id}, tipo={self.tipo_evento}, fecha={self.fecha})"

# Modelo para la configuración del sistema de facturación
class ConfiguracionFacturacion(Base):
    __tablename__ = "configuracion_facturacion"
    
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(100), nullable=False)
    nombre_fantasia = Column(String(100))
    cuit = Column(String(13), nullable=False)
    ingresos_brutos = Column(String(20))
    inicio_actividades = Column(DateTime)
    condicion_iva = Column(Enum(CondicionIVA), nullable=False)
    direccion = Column(String(200))
    localidad = Column(String(100))
    provincia = Column(String(100))
    codigo_postal = Column(String(10))
    telefono = Column(String(20))
    email = Column(String(100))
    logo_path = Column(String(255))
    certificado_path = Column(String(255))
    clave_path = Column(String(255))
    ws_wsdl = Column(String(255))
    homo = Column(Boolean, default=True)  # True para homologación, False para producción
    
    def __repr__(self):
        return f"ConfiguracionFacturacion(id={self.id}, razon_social={self.razon_social}, cuit={self.cuit})"