# ============================================================================
# SERVICE: CATEGORIA_7306
# ============================================================================
"""
Service para categoria_7306
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_categoria_7306 import Categoria7306
from .schema_categoria_7306 import Categoria_7306Create, Categoria_7306Update

class Categoria_7306Service:
    """Service para operaciones CRUD de categoria_7306"""
    
    def create(self, db: Session, obj_in: Categoria_7306Create) -> Categoria7306:
        """Crear nuevo registro de categoria_7306"""
        obj_data = obj_in.model_dump()
        db_obj = Categoria7306(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Categoria7306]:
        """Obtener categoria_7306 por id"""
        return db.query(Categoria7306).filter(Categoria7306.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Categoria7306]:
        """Obtener múltiples registros de categoria_7306"""
        return db.query(Categoria7306).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Categoria7306, obj_in: Categoria_7306Update) -> Categoria7306:
        """Actualizar categoria_7306"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar categoria_7306"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
categoria_7306_service = Categoria_7306Service()
