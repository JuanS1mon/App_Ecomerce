# ============================================================================
# SERVICE: AUTORES
# ============================================================================
"""
Service para autores
Parte del servicio: biblioteca_sistema
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_autores import Autores
from .schema_autores import AutoresCreate, AutoresUpdate

class AutoresService:
    """Service para operaciones CRUD de autores"""
    
    def create(self, db: Session, obj_in: AutoresCreate) -> Autores:
        """Crear nuevo registro de autores"""
        obj_data = obj_in.model_dump()
        db_obj = Autores(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Autores]:
        """Obtener autores por id"""
        return db.query(Autores).filter(Autores.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Autores]:
        """Obtener múltiples registros de autores"""
        return db.query(Autores).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Autores, obj_in: AutoresUpdate) -> Autores:
        """Actualizar autores"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar autores"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
autores_service = AutoresService()
