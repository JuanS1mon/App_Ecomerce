# ============================================================================
# SERVICE: PRODUCTO_7306
# ============================================================================
"""
Service para producto_7306
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_producto_7306 import Producto7306
from .schema_producto_7306 import Producto_7306Create, Producto_7306Update

class Producto_7306Service:
    """Service para operaciones CRUD de producto_7306"""
    
    def create(self, db: Session, obj_in: Producto_7306Create) -> Producto7306:
        """Crear nuevo registro de producto_7306"""
        obj_data = obj_in.model_dump()
        db_obj = Producto7306(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Producto7306]:
        """Obtener producto_7306 por id"""
        return db.query(Producto7306).filter(Producto7306.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Producto7306]:
        """Obtener múltiples registros de producto_7306"""
        return db.query(Producto7306).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Producto7306, obj_in: Producto_7306Update) -> Producto7306:
        """Actualizar producto_7306"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar producto_7306"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
producto_7306_service = Producto_7306Service()
