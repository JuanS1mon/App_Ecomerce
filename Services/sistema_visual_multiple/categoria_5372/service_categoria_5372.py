# ============================================================================
# SERVICE: CATEGORIA_5372
# ============================================================================
"""
Service para categoria_5372
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_categoria_5372 import Categoria5372
from .schema_categoria_5372 import Categoria_5372Create, Categoria_5372Update

class Categoria_5372Service:
    """Service para operaciones CRUD de categoria_5372"""
    
    def create(self, db: Session, obj_in: Categoria_5372Create) -> Categoria5372:
        """Crear nuevo registro de categoria_5372"""
        obj_data = obj_in.model_dump()
        db_obj = Categoria5372(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Categoria5372]:
        """Obtener categoria_5372 por id"""
        return db.query(Categoria5372).filter(Categoria5372.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Categoria5372]:
        """Obtener múltiples registros de categoria_5372"""
        return db.query(Categoria5372).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Categoria5372, obj_in: Categoria_5372Update) -> Categoria5372:
        """Actualizar categoria_5372"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar categoria_5372"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
categoria_5372_service = Categoria_5372Service()
