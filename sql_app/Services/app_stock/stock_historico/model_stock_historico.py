from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Stock_historico(Base):
    __tablename__ = 'stock_historico'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nro_movimiento = Column(Integer, default=0)
    codigo_art = Column(Integer, default=0)
    id_articulos_serie = Column(Integer, default=0)
    id_deposito = Column(Integer, default=0)
    cant_disponible = Column(Float, default=0.0)
    cant_reservado = Column(Float, default=0.0)
    cant_preparado = Column(Float, default=0.0)
    tipo = Column(Boolean, default=False)
    fecha = Column(String(255))
    observacion = Column(String(255))
