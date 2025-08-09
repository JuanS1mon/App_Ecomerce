# ============================================================================
# SERVICE: DETALLE_ORDEN
# ============================================================================
"""
Service para detalle_orden
Parte del servicio: ecommerce_app
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_detalle_orden import DetalleOrden
from .schema_detalle_orden import Detalle_OrdenCreate, Detalle_OrdenUpdate

class Detalle_OrdenService:
    """Service para operaciones CRUD de detalle_orden"""
    
    def create(self, db: Session, obj_in: Detalle_OrdenCreate) -> DetalleOrden:
        """Crear nuevo registro de detalle_orden"""
        obj_data = obj_in.model_dump()
        db_obj = DetalleOrden(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden]:
        """Obtener detalle_orden por id"""
        return db.query(DetalleOrden).filter(DetalleOrden.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden]:
        """Obtener múltiples registros de detalle_orden"""
        return db.query(DetalleOrden).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: DetalleOrden, obj_in: Detalle_OrdenUpdate) -> DetalleOrden:
        """Actualizar detalle_orden"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
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

# Instancia global del service
detalle_orden_service = Detalle_OrdenService()
