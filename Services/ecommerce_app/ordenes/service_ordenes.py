# ============================================================================
# SERVICE: ORDENES
# ============================================================================
"""
Service para ordenes
Parte del servicio: ecommerce_app
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_ordenes import Ordenes
from .schema_ordenes import OrdenesCreate, OrdenesUpdate

class OrdenesService:
    """Service para operaciones CRUD de ordenes"""
    
    def create(self, db: Session, obj_in: OrdenesCreate) -> Ordenes:
        """Crear nuevo registro de ordenes"""
        obj_data = obj_in.model_dump()
        db_obj = Ordenes(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Ordenes]:
        """Obtener ordenes por id"""
        return db.query(Ordenes).filter(Ordenes.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Ordenes]:
        """Obtener múltiples registros de ordenes"""
        return db.query(Ordenes).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Ordenes, obj_in: OrdenesUpdate) -> Ordenes:
        """Actualizar ordenes"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar ordenes"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
ordenes_service = OrdenesService()
