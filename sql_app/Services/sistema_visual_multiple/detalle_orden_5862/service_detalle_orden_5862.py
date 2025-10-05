# ============================================================================
# SERVICE: DETALLE_ORDEN_5862
# ============================================================================
"""
Service para detalle_orden_5862
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_detalle_orden_5862 import DetalleOrden5862
from .schema_detalle_orden_5862 import Detalle_Orden_5862Create, Detalle_Orden_5862Update

class Detalle_Orden_5862Service:
    """Service para operaciones CRUD de detalle_orden_5862"""
    
    def create(self, db: Session, obj_in: Detalle_Orden_5862Create) -> DetalleOrden5862:
        """Crear nuevo registro de detalle_orden_5862"""
        obj_data = obj_in.model_dump()
        db_obj = DetalleOrden5862(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden5862]:
        """Obtener detalle_orden_5862 por id"""
        return db.query(DetalleOrden5862).filter(DetalleOrden5862.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden5862]:
        """Obtener múltiples registros de detalle_orden_5862"""
        return db.query(DetalleOrden5862).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: DetalleOrden5862, obj_in: Detalle_Orden_5862Update) -> DetalleOrden5862:
        """Actualizar detalle_orden_5862"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar detalle_orden_5862"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
detalle_orden_5862_service = Detalle_Orden_5862Service()
