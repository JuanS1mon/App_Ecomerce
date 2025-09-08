# ============================================================================
# SERVICE: PRODUCTO_4096
# ============================================================================
"""
Service para producto_4096
Parte del servicio: sist1
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_producto_4096 import Producto4096
from .schema_producto_4096 import Producto_4096Create, Producto_4096Update

class Producto_4096Service:
    """Service para operaciones CRUD de producto_4096"""
    
    def create(self, db: Session, obj_in: Producto_4096Create) -> Producto4096:
        """Crear nuevo registro de producto_4096"""
        obj_data = obj_in.model_dump()
        db_obj = Producto4096(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Producto4096]:
        """Obtener producto_4096 por id"""
        return db.query(Producto4096).filter(Producto4096.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Producto4096]:
        """Obtener múltiples registros de producto_4096"""
        return db.query(Producto4096).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Producto4096, obj_in: Producto_4096Update) -> Producto4096:
        """Actualizar producto_4096"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar producto_4096"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
producto_4096_service = Producto_4096Service()
