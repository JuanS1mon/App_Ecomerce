# ============================================================================
# SERVICE: PRODUCTO_2650
# ============================================================================
"""
Service para producto_2650
Parte del servicio: dm3
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_producto_2650 import Producto2650
from .schema_producto_2650 import Producto_2650Create, Producto_2650Update

class Producto_2650Service:
    """Service para operaciones CRUD de producto_2650"""
    
    def create(self, db: Session, obj_in: Producto_2650Create) -> Producto2650:
        """Crear nuevo registro de producto_2650"""
        obj_data = obj_in.model_dump()
        db_obj = Producto2650(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Producto2650]:
        """Obtener producto_2650 por id"""
        return db.query(Producto2650).filter(Producto2650.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Producto2650]:
        """Obtener múltiples registros de producto_2650"""
        return db.query(Producto2650).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Producto2650, obj_in: Producto_2650Update) -> Producto2650:
        """Actualizar producto_2650"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar producto_2650"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
producto_2650_service = Producto_2650Service()
