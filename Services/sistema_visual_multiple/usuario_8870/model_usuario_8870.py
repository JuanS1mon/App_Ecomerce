# ============================================================================
# MODELO: USUARIO_8870
# ============================================================================
"""
Modelo para usuario_8870
Parte del servicio: sistema_visual_multiple
Módulo usuario_8870 generado desde Editor Visual
"""

from sqlalchemy import Column, Integer, String, Boolean
from sql_app.db.database import Base

class Usuario8870(Base):
    """
    Modelo para usuario_8870
    Módulo usuario_8870 generado desde Editor Visual
    """
    __tablename__ = "usuario_8870"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefono = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Usuario8870(id={self.id})>"
