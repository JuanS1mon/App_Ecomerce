from sqlalchemy import Column, Integer, ForeignKey
from db.database import Base

class usuarios_rol(Base):
    __tablename__ = "UsuariosRol"  # Ajustar al nombre real de la tabla en SQL Server
    
    usuario_id = Column(Integer, ForeignKey("Usuarios.codigo", ondelete="CASCADE"), primary_key=True)
    rol_id = Column(Integer, ForeignKey("Roles.id", ondelete="CASCADE"), primary_key=True)