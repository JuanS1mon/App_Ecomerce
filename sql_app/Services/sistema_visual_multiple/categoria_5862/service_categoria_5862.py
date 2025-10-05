# ============================================================================
# SERVICE: CATEGORIA_5862
# ============================================================================
"""
Service para categoria_5862
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_categoria_5862 import Categoria5862
from .schema_categoria_5862 import Categoria_5862Create, Categoria_5862Update

class Categoria_5862Service:
    """Service para operaciones CRUD de categoria_5862"""
    
    def create(self, db: Session, obj_in: Categoria_5862Create) -> Categoria5862:
        """Crear nuevo registro de categoria_5862"""
        obj_data = obj_in.model_dump()
        db_obj = Categoria5862(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Categoria5862]:
        """Obtener categoria_5862 por id"""
        return db.query(Categoria5862).filter(Categoria5862.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Categoria5862]:
        """Obtener múltiples registros de categoria_5862"""
        return db.query(Categoria5862).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Categoria5862, obj_in: Categoria_5862Update) -> Categoria5862:
        """Actualizar categoria_5862"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar categoria_5862"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
categoria_5862_service = Categoria_5862Service()
