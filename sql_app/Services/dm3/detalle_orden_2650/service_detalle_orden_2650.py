# ============================================================================
# SERVICE: DETALLE_ORDEN_2650
# ============================================================================
"""
Service para detalle_orden_2650
Parte del servicio: dm3
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_detalle_orden_2650 import DetalleOrden2650
from .schema_detalle_orden_2650 import Detalle_Orden_2650Create, Detalle_Orden_2650Update

class Detalle_Orden_2650Service:
    """Service para operaciones CRUD de detalle_orden_2650"""
    
    def create(self, db: Session, obj_in: Detalle_Orden_2650Create) -> DetalleOrden2650:
        """Crear nuevo registro de detalle_orden_2650"""
        obj_data = obj_in.model_dump()
        db_obj = DetalleOrden2650(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[DetalleOrden2650]:
        """Obtener detalle_orden_2650 por id"""
        return db.query(DetalleOrden2650).filter(DetalleOrden2650.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[DetalleOrden2650]:
        """Obtener múltiples registros de detalle_orden_2650"""
        return db.query(DetalleOrden2650).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: DetalleOrden2650, obj_in: Detalle_Orden_2650Update) -> DetalleOrden2650:
        """Actualizar detalle_orden_2650"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar detalle_orden_2650"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
detalle_orden_2650_service = Detalle_Orden_2650Service()
