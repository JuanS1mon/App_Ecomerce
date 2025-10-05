# ============================================================================
# SERVICE: RECETAS
# ============================================================================
"""
Service para recetas
Parte del servicio: pizzeria_one_man_company
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_recetas import Recetas
from .schema_recetas import RecetasCreate, RecetasUpdate

class RecetasService:
    """Service para operaciones CRUD de recetas"""
    
    def create(self, db: Session, obj_in: RecetasCreate) -> Recetas:
        """Crear nuevo registro de recetas"""
        obj_data = obj_in.model_dump()
        db_obj = Recetas(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Recetas]:
        """Obtener recetas por id"""
        return db.query(Recetas).filter(Recetas.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Recetas]:
        """Obtener múltiples registros de recetas"""
        return db.query(Recetas).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Recetas, obj_in: RecetasUpdate) -> Recetas:
        """Actualizar recetas"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar recetas"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
recetas_service = RecetasService()
