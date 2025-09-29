# ============================================================================
# SERVICE: ORDEN_7306
# ============================================================================
"""
Service para orden_7306
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_orden_7306 import Orden7306
from .schema_orden_7306 import Orden_7306Create, Orden_7306Update

class Orden_7306Service:
    """Service para operaciones CRUD de orden_7306"""
    
    def create(self, db: Session, obj_in: Orden_7306Create) -> Orden7306:
        """Crear nuevo registro de orden_7306"""
        obj_data = obj_in.model_dump()
        db_obj = Orden7306(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Orden7306]:
        """Obtener orden_7306 por id"""
        return db.query(Orden7306).filter(Orden7306.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Orden7306]:
        """Obtener múltiples registros de orden_7306"""
        return db.query(Orden7306).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Orden7306, obj_in: Orden_7306Update) -> Orden7306:
        """Actualizar orden_7306"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar orden_7306"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
orden_7306_service = Orden_7306Service()
