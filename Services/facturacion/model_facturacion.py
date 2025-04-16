from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from db.database import Base
from datetime import datetime

class Facturacion(Base):
    __tablename__ = 'facturacion'

    # Campos de identificación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nrofactura = Column(String(13), unique=True, nullable=False, index=True)
    
    # Tipo de comprobante (A, B, C, etc.)
    tipo_comprobante = Column(String(1), nullable=False, index=True)
    
    # Información general
    fecha_emision = Column(Date, nullable=False, default=datetime.now().date)
    fecha_vencimiento = Column(Date, nullable=True)
    
    # Información del emisor (vendedor)
    emisor_razon_social = Column(String(100), nullable=False)
    emisor_nombre_fantasia = Column(String(100), nullable=True)
    emisor_cuit = Column(String(13), nullable=False)  # Formato: 00-00000000-0
    emisor_domicilio = Column(String(200), nullable=False)
    emisor_localidad = Column(String(100), nullable=False)
    emisor_provincia = Column(String(50), nullable=False)
    emisor_codigo_postal = Column(String(10), nullable=False)
    emisor_condicion_iva = Column(String(50), nullable=False)  # Responsable Inscripto, Monotributo, etc.
    emisor_ingresos_brutos = Column(String(20), nullable=True)
    emisor_inicio_actividades = Column(Date, nullable=True)
    
    # Información del receptor (cliente/comprador)
    receptor_tipo_documento = Column(String(20), nullable=False, default="CUIT")  # CUIT, DNI, etc.
    receptor_nro_documento = Column(String(20), nullable=False)
    receptor_razon_social = Column(String(100), nullable=False)
    receptor_domicilio = Column(String(200), nullable=True)
    receptor_localidad = Column(String(100), nullable=True)
    receptor_provincia = Column(String(50), nullable=True)
    receptor_codigo_postal = Column(String(10), nullable=True)
    receptor_condicion_iva = Column(String(50), nullable=False)  # Responsable Inscripto, Consumidor Final, etc.
    
    # Información de pago
    condicion_venta = Column(String(50), nullable=False, default="Contado")  # Contado, Cuenta Corriente, etc.
    forma_pago = Column(String(50), nullable=True)  # Efectivo, Transferencia, Tarjeta, etc.
    
    # Importes
    moneda = Column(String(3), nullable=False, default="ARS")
    tipo_cambio = Column(Numeric(10, 4), nullable=False, default=1.0)
    subtotal = Column(Numeric(12, 2), nullable=False, default=0.0)
    descuento_porcentaje = Column(Numeric(5, 2), nullable=True)
    descuento_importe = Column(Numeric(12, 2), nullable=True, default=0.0)
    subtotal_neto = Column(Numeric(12, 2), nullable=False, default=0.0)  # Subtotal - descuento
    iva_porcentaje = Column(Numeric(5, 2), nullable=False, default=21.0)
    iva_importe = Column(Numeric(12, 2), nullable=False, default=0.0)
    otros_impuestos = Column(Numeric(12, 2), nullable=True, default=0.0)
    total = Column(Numeric(12, 2), nullable=False, default=0.0)
    
    # CAE (Código de Autorización Electrónica)
    cae = Column(String(14), nullable=True)
    cae_vencimiento = Column(Date, nullable=True)
    
    # Estado de la factura
    estado = Column(String(20), nullable=False, default="Borrador")  # Borrador, Emitida, Anulada, Pagada
    
    # Información adicional
    observaciones = Column(Text, nullable=True)
    
    # Información de auditoría
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    anulada = Column(Boolean, default=False)

class FacturaItem(Base):
    __tablename__ = 'factura_items'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factura_id = Column(Integer, ForeignKey('facturacion.id', ondelete='CASCADE'), nullable=False)
    
    # Información del producto/servicio
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(200), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False, default=1.0)
    unidad_medida = Column(String(20), nullable=True, default="unidad")
    
    # Precios e importes
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    bonificacion_porcentaje = Column(Numeric(5, 2), nullable=True, default=0.0)
    subtotal = Column(Numeric(12, 2), nullable=False)
    alicuota_iva = Column(Numeric(5, 2), nullable=False, default=21.0)
    importe_iva = Column(Numeric(12, 2), nullable=False)
    importe_total = Column(Numeric(12, 2), nullable=False)
    
    # Información adicional
    observaciones = Column(Text, nullable=True)
