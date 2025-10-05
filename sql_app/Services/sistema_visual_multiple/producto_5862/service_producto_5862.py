# ============================================================================
# SERVICE: PRODUCTO_5862
# ============================================================================
"""
Service para producto_5862
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_producto_5862 import Producto5862
from .schema_producto_5862 import Producto_5862Create, Producto_5862Update

class Producto_5862Service:
    """Service para operaciones CRUD de producto_5862"""
    
    def create(self, db: Session, obj_in: Producto_5862Create) -> Producto5862:
        """Crear nuevo registro de producto_5862"""
        obj_data = obj_in.model_dump()
        db_obj = Producto5862(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Producto5862]:
        """Obtener producto_5862 por id"""
        return db.query(Producto5862).filter(Producto5862.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Producto5862]:
        """Obtener múltiples registros de producto_5862"""
        return db.query(Producto5862).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Producto5862, obj_in: Producto_5862Update) -> Producto5862:
        """Actualizar producto_5862"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar producto_5862"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
producto_5862_service = Producto_5862Service()
