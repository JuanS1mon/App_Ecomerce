# ============================================================================
# SERVICE: PEDIDOS
# ============================================================================
"""
Service para pedidos
Parte del servicio: pizzeria_one_man_company
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_pedidos import Pedidos
from .schema_pedidos import PedidosCreate, PedidosUpdate

class PedidosService:
    """Service para operaciones CRUD de pedidos"""
    
    def create(self, db: Session, obj_in: PedidosCreate) -> Pedidos:
        """Crear nuevo registro de pedidos"""
        obj_data = obj_in.model_dump()
        db_obj = Pedidos(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Pedidos]:
        """Obtener pedidos por id"""
        return db.query(Pedidos).filter(Pedidos.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Pedidos]:
        """Obtener múltiples registros de pedidos"""
        return db.query(Pedidos).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Pedidos, obj_in: PedidosUpdate) -> Pedidos:
        """Actualizar pedidos"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar pedidos"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
pedidos_service = PedidosService()
