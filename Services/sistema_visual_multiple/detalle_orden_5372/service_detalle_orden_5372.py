# ============================================================================
# SERVICE: DETALLE_ORDEN_5372
# ============================================================================
"""
Service para detalle_orden_5372
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_detalle_orden_5372 import DetalleOrden5372
from .schema_detalle_orden_5372 import Detalle_Orden_5372Create, Detalle_Orden_5372Update

class Detalle_Orden_5372Service:
    """Service para operaciones CRUD de detalle_orden_5372"""
    
    def create(self, db: Session, obj_in: Detalle_Orden_5372Create) -> DetalleOrden5372:
        """Crear nuevo registro de detalle_orden_5372"""
        obj_data = obj_in.model_dump()
        db_obj = DetalleOrden5372(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden5372]:
        """Obtener detalle_orden_5372 por id"""
        return db.query(DetalleOrden5372).filter(DetalleOrden5372.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden5372]:
        """Obtener múltiples registros de detalle_orden_5372"""
        return db.query(DetalleOrden5372).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: DetalleOrden5372, obj_in: Detalle_Orden_5372Update) -> DetalleOrden5372:
        """Actualizar detalle_orden_5372"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar detalle_orden_5372"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
detalle_orden_5372_service = Detalle_Orden_5372Service()
