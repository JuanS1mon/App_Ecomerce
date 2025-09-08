# ============================================================================
# SERVICE: ORDEN_5372
# ============================================================================
"""
Service para orden_5372
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_orden_5372 import Orden5372
from .schema_orden_5372 import Orden_5372Create, Orden_5372Update

class Orden_5372Service:
    """Service para operaciones CRUD de orden_5372"""
    
    def create(self, db: Session, obj_in: Orden_5372Create) -> Orden5372:
        """Crear nuevo registro de orden_5372"""
        obj_data = obj_in.model_dump()
        db_obj = Orden5372(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Orden5372]:
        """Obtener orden_5372 por id"""
        return db.query(Orden5372).filter(Orden5372.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Orden5372]:
        """Obtener múltiples registros de orden_5372"""
        return db.query(Orden5372).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Orden5372, obj_in: Orden_5372Update) -> Orden5372:
        """Actualizar orden_5372"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar orden_5372"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
orden_5372_service = Orden_5372Service()
