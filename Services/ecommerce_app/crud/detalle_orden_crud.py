# ============================================================================
# CRUD PARA TABLA: DETALLE_ORDEN
# ============================================================================
"""
Operaciones CRUD para detalle_orden
Parte del servicio multi-tabla: ecommerce_app
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..ecommerce_app_models import DetalleOrden

class DetalleOrdenCRUD:
    """Operaciones CRUD para DetalleOrden"""
    
    def create(self, db: Session, **kwargs) -> DetalleOrden:
        """Crear nuevo registro de detalle_orden"""
        db_obj = DetalleOrden(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden]:
        """Obtener detalle_orden por id"""
        return db.query(DetalleOrden).filter(DetalleOrden.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden]:
        """Obtener todos los registros de detalle_orden"""
        return db.query(DetalleOrden).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[DetalleOrden]:
        """Actualizar detalle_orden"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar detalle_orden"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
detalle_orden_crud = DetalleOrdenCRUD()
