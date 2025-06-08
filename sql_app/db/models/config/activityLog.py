# Imports de bibliotecas estándar
import datetime

# Imports de terceros
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

# Imports del proyecto
from ...database import Base

class ActivityLog(Base):
    __tablename__ = "activity_log"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey("Usuarios.codigo"))  # Debe ser user_id, no usuario_id