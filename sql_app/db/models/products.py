from sqlalchemy import Column, Integer, String, Boolean, Float
from ..database import Base

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, default=0)
    name = Column(String(50), default=' ')
    sku = Column(String(50), default=' ')
    barcode = Column(Float, default=0.0)
    quantity = Column(String(50), default=' ')
    category = Column(String(50), default=' ')
    location = Column(String(50), default=' ')
    minimunstock = Column(Float, default=0.0)
    maximumstock = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    supplier = Column(String(50), default=' ')
    brand = Column(String(50), default=' ')
    lastupdate = Column(String(50), default=' ')
