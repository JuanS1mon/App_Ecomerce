# ============================================================================
# SERVICE: PRODUCTO_5372
# ============================================================================
"""
Service para producto_5372
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_producto_5372 import Producto5372
from .schema_producto_5372 import Producto_5372Create, Producto_5372Update

class Producto_5372Service:
    """Service para operaciones CRUD de producto_5372"""
    
    def create(self, db: Session, obj_in: Producto_5372Create) -> Producto5372:
        """Crear nuevo registro de producto_5372"""
        obj_data = obj_in.model_dump()
        db_obj = Producto5372(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Producto5372]:
        """Obtener producto_5372 por id"""
        return db.query(Producto5372).filter(Producto5372.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Producto5372]:
        """Obtener múltiples registros de producto_5372"""
        return db.query(Producto5372).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Producto5372, obj_in: Producto_5372Update) -> Producto5372:
        """Actualizar producto_5372"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar producto_5372"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
producto_5372_service = Producto_5372Service()
