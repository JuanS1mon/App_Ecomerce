# ============================================================================
# SERVICE: DETALLE_ORDEN_7306
# ============================================================================
"""
Service para detalle_orden_7306
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_detalle_orden_7306 import DetalleOrden7306
from .schema_detalle_orden_7306 import Detalle_Orden_7306Create, Detalle_Orden_7306Update

class Detalle_Orden_7306Service:
    """Service para operaciones CRUD de detalle_orden_7306"""
    
    def create(self, db: Session, obj_in: Detalle_Orden_7306Create) -> DetalleOrden7306:
        """Crear nuevo registro de detalle_orden_7306"""
        obj_data = obj_in.model_dump()
        db_obj = DetalleOrden7306(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden7306]:
        """Obtener detalle_orden_7306 por id"""
        return db.query(DetalleOrden7306).filter(DetalleOrden7306.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden7306]:
        """Obtener múltiples registros de detalle_orden_7306"""
        return db.query(DetalleOrden7306).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: DetalleOrden7306, obj_in: Detalle_Orden_7306Update) -> DetalleOrden7306:
        """Actualizar detalle_orden_7306"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar detalle_orden_7306"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
detalle_orden_7306_service = Detalle_Orden_7306Service()
