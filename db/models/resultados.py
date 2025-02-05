from sqlalchemy import Column, Integer, String, Float, DateTime
from ..database import Base  # Asegúrate de importar Base desde el archivo correcto

class ResultadoKPI(Base):
    __tablename__ = 'resultados_kpi'
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(255), index=True)  # Especificar la longitud de la columna
    total_registros = Column(Integer)
    categorias = Column(Integer)
    last_date = Column(DateTime)
    first_date = Column(DateTime)
    max_value = Column(Float)
    min_value = Column(Float)
    clusters = Column(String)  # Puedes ajustar esto según cómo quieras almacenar los clusters