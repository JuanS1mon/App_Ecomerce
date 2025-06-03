from sqlalchemy import Column, Integer, NVARCHAR, Boolean

try:
    from ...database import Base
except ImportError:
    from sql_app.db.database import Base

class usuarios(Base):
    __tablename__ = 'Usuarios'  # Asegúrate de que coincida con el nombre real en la base de datos

    codigo = Column(Integer, primary_key=True, index=True, autoincrement=False)
    usuario = Column(NVARCHAR(50), unique=True, nullable=False)
    nombre = Column(NVARCHAR(100), nullable=False)
    mail = Column(NVARCHAR(100), unique=True, nullable=False)
    activo = Column(Boolean(create_constraint=False), default=True)
    clave = Column(NVARCHAR(250), nullable=False)
    