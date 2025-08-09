# ============================================================================
# CRUD PARA TABLA: PEDIDOS123
# ============================================================================
"""
Operaciones CRUD para pedidos123
Parte del servicio multi-tabla: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..sistema_visual_multiple_models import Pedidos123

class Pedidos123CRUD:
    """Operaciones CRUD para Pedidos123"""
    
    def create(self, db: Session, **kwargs) -> Pedidos123:
        """Crear nuevo registro de pedidos123"""
        db_obj = Pedidos123(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Pedidos123]:
        """Obtener pedidos123 por id"""
        return db.query(Pedidos123).filter(Pedidos123.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Pedidos123]:
        """Obtener todos los registros de pedidos123"""
        return db.query(Pedidos123).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[Pedidos123]:
        """Actualizar pedidos123"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar pedidos123"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
pedidos123_crud = Pedidos123CRUD()
