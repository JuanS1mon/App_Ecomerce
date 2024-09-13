from sqlalchemy import Column, Integer, NVARCHAR, Boolean, Float
from ..database import Base


class transactiones(Base):
    __tablename__ = 'transactiones'

    id = Column(Integer, primary_key=True, index=True, default=0)
    producto_id = Column(Integer, primary_key=True, index=True, default=0)
    cantidad = Column(Float, default=0.0)
    transaction_tipo = Column(NVARCHAR(50), default=' ')
    transaction_date = Column(NVARCHAR(50), default=' ')
    usuario_id = Column(Integer, primary_key=True, index=True, default=0)
    created_at = Column(NVARCHAR(50), default=' ')
    updated_at = Column(NVARCHAR(50), default=' ')
