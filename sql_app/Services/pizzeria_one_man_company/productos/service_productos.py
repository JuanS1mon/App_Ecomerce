# ============================================================================
# SERVICE: PRODUCTOS
# ============================================================================
"""
Service para productos
Parte del servicio: pizzeria_one_man_company
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_productos import Productos
from .schema_productos import ProductosCreate, ProductosUpdate

class ProductosService:
    """Service para operaciones CRUD de productos"""
    
    def create(self, db: Session, obj_in: ProductosCreate) -> Productos:
        """Crear nuevo registro de productos"""
        obj_data = obj_in.model_dump()
        db_obj = Productos(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Productos]:
        """Obtener productos por id"""
        return db.query(Productos).filter(Productos.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Productos]:
        """Obtener múltiples registros de productos"""
        return db.query(Productos).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Productos, obj_in: ProductosUpdate) -> Productos:
        """Actualizar productos"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
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

# Instancia global del service
productos_service = ProductosService()
