# ============================================================================
# SERVICE: ORDEN_4096
# ============================================================================
"""
Service para orden_4096
Parte del servicio: sist1
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_orden_4096 import Orden4096
from .schema_orden_4096 import Orden_4096Create, Orden_4096Update

class Orden_4096Service:
    """Service para operaciones CRUD de orden_4096"""
    
    def create(self, db: Session, obj_in: Orden_4096Create) -> Orden4096:
        """Crear nuevo registro de orden_4096"""
        obj_data = obj_in.model_dump()
        db_obj = Orden4096(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Orden4096]:
        """Obtener orden_4096 por id"""
        return db.query(Orden4096).filter(Orden4096.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Orden4096]:
        """Obtener múltiples registros de orden_4096"""
        return db.query(Orden4096).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Orden4096, obj_in: Orden_4096Update) -> Orden4096:
        """Actualizar orden_4096"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar orden_4096"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
orden_4096_service = Orden_4096Service()
