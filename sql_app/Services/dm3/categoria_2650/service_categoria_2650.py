# ============================================================================
# SERVICE: CATEGORIA_2650
# ============================================================================
"""
Service para categoria_2650
Parte del servicio: dm3
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_categoria_2650 import Categoria2650
from .schema_categoria_2650 import Categoria_2650Create, Categoria_2650Update

class Categoria_2650Service:
    """Service para operaciones CRUD de categoria_2650"""
    
    def create(self, db: Session, obj_in: Categoria_2650Create) -> Categoria2650:
        """Crear nuevo registro de categoria_2650"""
        obj_data = obj_in.model_dump()
        db_obj = Categoria2650(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Categoria2650]:
        """Obtener categoria_2650 por id"""
        return db.query(Categoria2650).filter(Categoria2650.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Categoria2650]:
        """Obtener múltiples registros de categoria_2650"""
        return db.query(Categoria2650).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Categoria2650, obj_in: Categoria_2650Update) -> Categoria2650:
        """Actualizar categoria_2650"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar categoria_2650"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
categoria_2650_service = Categoria_2650Service()
