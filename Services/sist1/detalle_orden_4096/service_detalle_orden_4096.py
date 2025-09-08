# ============================================================================
# SERVICE: DETALLE_ORDEN_4096
# ============================================================================
"""
Service para detalle_orden_4096
Parte del servicio: sist1
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_detalle_orden_4096 import DetalleOrden4096
from .schema_detalle_orden_4096 import Detalle_Orden_4096Create, Detalle_Orden_4096Update

class Detalle_Orden_4096Service:
    """Service para operaciones CRUD de detalle_orden_4096"""
    
    def create(self, db: Session, obj_in: Detalle_Orden_4096Create) -> DetalleOrden4096:
        """Crear nuevo registro de detalle_orden_4096"""
        obj_data = obj_in.model_dump()
        db_obj = DetalleOrden4096(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden4096]:
        """Obtener detalle_orden_4096 por id"""
        return db.query(DetalleOrden4096).filter(DetalleOrden4096.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden4096]:
        """Obtener múltiples registros de detalle_orden_4096"""
        return db.query(DetalleOrden4096).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: DetalleOrden4096, obj_in: Detalle_Orden_4096Update) -> DetalleOrden4096:
        """Actualizar detalle_orden_4096"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar detalle_orden_4096"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
detalle_orden_4096_service = Detalle_Orden_4096Service()
