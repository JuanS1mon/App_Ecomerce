# ============================================================================
# CRUD PARA TABLA: PRODUCTOS123
# ============================================================================
"""
Operaciones CRUD para productos123
Parte del servicio multi-tabla: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..sistema_visual_multiple_models import Productos123

class Productos123CRUD:
    """Operaciones CRUD para Productos123"""
    
    def create(self, db: Session, **kwargs) -> Productos123:
        """Crear nuevo registro de productos123"""
        db_obj = Productos123(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Productos123]:
        """Obtener productos123 por id"""
        return db.query(Productos123).filter(Productos123.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Productos123]:
        """Obtener todos los registros de productos123"""
        return db.query(Productos123).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[Productos123]:
        """Actualizar productos123"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar productos123"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
productos123_crud = Productos123CRUD()
