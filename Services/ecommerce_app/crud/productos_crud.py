# ============================================================================
# CRUD PARA TABLA: PRODUCTOS
# ============================================================================
"""
Operaciones CRUD para productos
Parte del servicio multi-tabla: ecommerce_app
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..ecommerce_app_models import Productos

class ProductosCRUD:
    """Operaciones CRUD para Productos"""
    
    def create(self, db: Session, **kwargs) -> Productos:
        """Crear nuevo registro de productos"""
        db_obj = Productos(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Productos]:
        """Obtener productos por id"""
        return db.query(Productos).filter(Productos.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Productos]:
        """Obtener todos los registros de productos"""
        return db.query(Productos).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[Productos]:
        """Actualizar productos"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar productos"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
productos_crud = ProductosCRUD()
