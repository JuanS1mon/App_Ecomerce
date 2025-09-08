# ============================================================================
# SERVICE: ORDEN_2650
# ============================================================================
"""
Service para orden_2650
Parte del servicio: dm3
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_orden_2650 import Orden2650
from .schema_orden_2650 import Orden_2650Create, Orden_2650Update

class Orden_2650Service:
    """Service para operaciones CRUD de orden_2650"""
    
    def create(self, db: Session, obj_in: Orden_2650Create) -> Orden2650:
        """Crear nuevo registro de orden_2650"""
        obj_data = obj_in.model_dump()
        db_obj = Orden2650(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Orden2650]:
        """Obtener orden_2650 por id"""
        return db.query(Orden2650).filter(Orden2650.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Orden2650]:
        """Obtener múltiples registros de orden_2650"""
        return db.query(Orden2650).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Orden2650, obj_in: Orden_2650Update) -> Orden2650:
        """Actualizar orden_2650"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar orden_2650"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
orden_2650_service = Orden_2650Service()
