# ============================================================================
# SERVICE: TAREAS
# ============================================================================
"""
Service para tareas
Parte del servicio: crm_empresarial
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_tareas import Tareas
from .schema_tareas import TareasCreate, TareasUpdate

class TareasService:
    """Service para operaciones CRUD de tareas"""
    
    def create(self, db: Session, obj_in: TareasCreate) -> Tareas:
        """Crear nuevo registro de tareas"""
        obj_data = obj_in.model_dump()
        db_obj = Tareas(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Tareas]:
        """Obtener tareas por id"""
        return db.query(Tareas).filter(Tareas.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Tareas]:
        """Obtener múltiples registros de tareas"""
        return db.query(Tareas).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Tareas, obj_in: TareasUpdate) -> Tareas:
        """Actualizar tareas"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar tareas"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
tareas_service = TareasService()
