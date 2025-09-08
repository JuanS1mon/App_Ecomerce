# ============================================================================
# SERVICE: TABLA1
# ============================================================================
"""
Service para tabla1
Parte del servicio: mi_sistema
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_tabla1 import Tabla1
from .schema_tabla1 import Tabla1Create, Tabla1Update

class Tabla1Service:
    """Service para operaciones CRUD de tabla1"""
    
    def create(self, db: Session, obj_in: Tabla1Create) -> Tabla1:
        """Crear nuevo registro de tabla1"""
        obj_data = obj_in.model_dump()
        db_obj = Tabla1(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Tabla1]:
        """Obtener tabla1 por id"""
        return db.query(Tabla1).filter(Tabla1.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Tabla1]:
        """Obtener múltiples registros de tabla1"""
        return db.query(Tabla1).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Tabla1, obj_in: Tabla1Update) -> Tabla1:
        """Actualizar tabla1"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar tabla1"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
tabla1_service = Tabla1Service()
