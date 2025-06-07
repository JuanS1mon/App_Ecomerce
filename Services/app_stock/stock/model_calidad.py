from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
try:
    from ....db.database import Base
except ImportError:
    from sql_app.db.database import Base
class CalidadBloqueo(Base):
    """
    Modelo para almacenar bloqueos de calidad sobre artículos en depósitos específicos.
    """
    __tablename__ = "stock_calidad_bloqueos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_deposito = Column(Integer, nullable=False)
    codigo_art = Column(Integer, nullable=False)
    cantidad = Column(Float, nullable=False, default=0.0)
    motivo = Column(String(255), nullable=True)
    fecha_bloqueo = Column(DateTime, default=datetime.now)
    fecha_liberacion = Column(DateTime, nullable=True)
    usuario_bloqueo = Column(String(100), nullable=True)
    usuario_liberacion = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    observaciones = Column(Text, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'fecha_bloqueo' not in kwargs:
            self.fecha_bloqueo = datetime.now()
        if 'activo' not in kwargs:
            self.activo = True
