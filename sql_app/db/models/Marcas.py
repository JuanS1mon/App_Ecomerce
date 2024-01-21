from sqlalchemy import Boolean, Column,Integer, String
from ..database import Base
#from sqlalchemy.orm import relationship


class Marcas(Base): #que es models.Base ?? https://docs.sqlalchemy.org/en/14/orm/extensions/declarative/api.html
    __tablename__ = "Marcas" # es la tabla que va a usar el modelo 

    codigo = Column(Integer, primary_key=True, autoincrement=True)
    Descripcion = Column(String)
    Tramsmitido = Column(Boolean, default=True)