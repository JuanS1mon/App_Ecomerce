# ============================================================================
# SERVICE: ORDEN_5862
# ============================================================================
"""
Service para orden_5862
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_orden_5862 import Orden5862
from .schema_orden_5862 import Orden_5862Create, Orden_5862Update

class Orden_5862Service:
    """Service para operaciones CRUD de orden_5862"""
    
    def create(self, db: Session, obj_in: Orden_5862Create) -> Orden5862:
        """Crear nuevo registro de orden_5862"""
        obj_data = obj_in.model_dump()
        db_obj = Orden5862(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Orden5862]:
        """Obtener orden_5862 por id"""
        return db.query(Orden5862).filter(Orden5862.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Orden5862]:
        """Obtener múltiples registros de orden_5862"""
        return db.query(Orden5862).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Orden5862, obj_in: Orden_5862Update) -> Orden5862:
        """Actualizar orden_5862"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar orden_5862"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
orden_5862_service = Orden_5862Service()
