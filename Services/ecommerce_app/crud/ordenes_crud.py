# ============================================================================
# CRUD PARA TABLA: ORDENES
# ============================================================================
"""
Operaciones CRUD para ordenes
Parte del servicio multi-tabla: ecommerce_app
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..ecommerce_app_models import Ordenes

class OrdenesCRUD:
    """Operaciones CRUD para Ordenes"""
    
    def create(self, db: Session, **kwargs) -> Ordenes:
        """Crear nuevo registro de ordenes"""
        db_obj = Ordenes(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Ordenes]:
        """Obtener ordenes por id"""
        return db.query(Ordenes).filter(Ordenes.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Ordenes]:
        """Obtener todos los registros de ordenes"""
        return db.query(Ordenes).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[Ordenes]:
        """Actualizar ordenes"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar ordenes"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
ordenes_crud = OrdenesCRUD()
