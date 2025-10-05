# ============================================================================
# SERVICE: INGREDIENTES
# ============================================================================
"""
Service para ingredientes
Parte del servicio: pizzeria_one_man_company
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_ingredientes import Ingredientes
from .schema_ingredientes import IngredientesCreate, IngredientesUpdate

class IngredientesService:
    """Service para operaciones CRUD de ingredientes"""
    
    def create(self, db: Session, obj_in: IngredientesCreate) -> Ingredientes:
        """Crear nuevo registro de ingredientes"""
        obj_data = obj_in.model_dump()
        db_obj = Ingredientes(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Ingredientes]:
        """Obtener ingredientes por id"""
        return db.query(Ingredientes).filter(Ingredientes.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Ingredientes]:
        """Obtener múltiples registros de ingredientes"""
        return db.query(Ingredientes).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Ingredientes, obj_in: IngredientesUpdate) -> Ingredientes:
        """Actualizar ingredientes"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar ingredientes"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
ingredientes_service = IngredientesService()
