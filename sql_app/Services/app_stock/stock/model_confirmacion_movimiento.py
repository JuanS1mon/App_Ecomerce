from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
try:
    from ...db.database import Base
except ImportError:
    from sql_app.db.database import Base
class ConfirmacionMovimiento(Base):
    """
    Modelo para almacenar confirmaciones de movimientos de stock.
    """
    __tablename__ = "confirmaciones_movimientos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nro_movimiento = Column(Integer, nullable=False)
    codigo_art = Column(Integer, nullable=False)
    cantidad = Column(Float, nullable=False, default=0.0)
    fecha = Column(DateTime, default=datetime.now)
    estado = Column(String(50), nullable=False, default="pendiente")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'fecha' not in kwargs:
            self.fecha = datetime.now()
