from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.codigo"))
    action = Column(String(255), index=True)  # Especificar longitud para la columna 'action'
    timestamp = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("usuarios", back_populates="activities")