# ============================================================================
# MODELOS MULTI-TABLA: ECOMMERCE_APP
# ============================================================================
"""
Sistema basico de e-commerce

Modelos generados automáticamente con relaciones:
- usuarios: 5 campos
- productos: 5 campos
- ordenes: 4 campos
- detalle_orden: 5 campos

Relaciones definidas: 3
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuarios(Base):
    """
    Modelo para usuarios
    Tabla de usuarios registrados
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, nullable=False)

    # Relaciones
    ordenes = relationship("Ordenes", back_populates="usuario")

    def __repr__(self):
        return f"<Usuarios(id={self.id})">


class Productos(Base):
    """
    Modelo para productos
    Catalogo de productos disponibles
    """
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # Relaciones
    detalles_producto = relationship("DetalleOrden", back_populates="producto")

    def __repr__(self):
        return f"<Productos(id={self.id})">


class Ordenes(Base):
    """
    Modelo para ordenes
    Ordenes realizadas por los usuarios
    """
    __tablename__ = "ordenes"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_orden = Column(DateTime, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    # Relaciones
    usuario = relationship("Usuarios", back_populates="ordenes")
    detalles = relationship("DetalleOrden", back_populates="orden")

    def __repr__(self):
        return f"<Ordenes(id={self.id})">


class DetalleOrden(Base):
    """
    Modelo para detalle_orden
    Detalle de productos en cada orden
    """
    __tablename__ = "detalle_orden"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    orden_id = Column(Integer, ForeignKey("ordenes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    # Relaciones
    orden = relationship("Ordenes", back_populates="detalles")
    producto = relationship("Productos", back_populates="detalles_producto")

    def __repr__(self):
        return f"<DetalleOrden(id={self.id})">


# ============================================================================
# FIN DE MODELOS PARA: ECOMMERCE_APP
# ============================================================================
