# ============================================================================
# SERVICE: T
# ============================================================================
"""
Service para t
Parte del servicio: test_service
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_t import T
from .schema_t import TCreate, TUpdate

class TService:
    """Service para operaciones CRUD de t"""
    
    def create(self, db: Session, obj_in: TCreate) -> T:
        """Crear nuevo registro de t"""
        obj_data = obj_in.model_dump()
        db_obj = T(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[T]:
        """Obtener t por id"""
        return db.query(T).filter(T.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtener múltiples registros de t"""
        return db.query(T).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: T, obj_in: TUpdate) -> T:
        """Actualizar t"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar t"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
t_service = TService()
