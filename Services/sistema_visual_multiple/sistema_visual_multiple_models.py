# ============================================================================
# MODELOS MULTI-TABLA: SISTEMA_VISUAL_MULTIPLE
# ============================================================================
"""
Sistema multi-tabla generado desde Editor Visual

Modelos generados automáticamente con relaciones:
- usuarios123: 5 campos
- productos123: 5 campos
- pedidos123: 5 campos

Relaciones definidas: 0
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class Usuarios123(Base):
    """
    Modelo para usuarios123
    Módulo usuarios123 generado desde Editor Visual
    """
    __tablename__ = "usuarios123"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    email = Column(String(255))
    activo = Column(Boolean)
    fecha_registro = Column(DateTime)

    def __repr__(self):
        return f"<Usuarios123(id={self.id})">


class Productos123(Base):
    """
    Modelo para productos123
    Módulo productos123 generado desde Editor Visual
    """
    __tablename__ = "productos123"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    precio = Column(Integer)
    disponible = Column(Boolean)
    categoria = Column(String(255))

    def __repr__(self):
        return f"<Productos123(id={self.id})">


class Pedidos123(Base):
    """
    Modelo para pedidos123
    Módulo pedidos123 generado desde Editor Visual
    """
    __tablename__ = "pedidos123"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer)
    producto_id = Column(Integer)
    cantidad = Column(Integer)
    fecha_pedido = Column(DateTime)

    def __repr__(self):
        return f"<Pedidos123(id={self.id})">


# ============================================================================
# FIN DE MODELOS PARA: SISTEMA_VISUAL_MULTIPLE
# ============================================================================
