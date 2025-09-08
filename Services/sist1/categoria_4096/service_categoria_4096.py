# ============================================================================
# SERVICE: CATEGORIA_4096
# ============================================================================
"""
Service para categoria_4096
Parte del servicio: sist1
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_categoria_4096 import Categoria4096
from .schema_categoria_4096 import Categoria_4096Create, Categoria_4096Update

class Categoria_4096Service:
    """Service para operaciones CRUD de categoria_4096"""
    
    def create(self, db: Session, obj_in: Categoria_4096Create) -> Categoria4096:
        """Crear nuevo registro de categoria_4096"""
        obj_data = obj_in.model_dump()
        db_obj = Categoria4096(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Categoria4096]:
        """Obtener categoria_4096 por id"""
        return db.query(Categoria4096).filter(Categoria4096.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Categoria4096]:
        """Obtener múltiples registros de categoria_4096"""
        return db.query(Categoria4096).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Categoria4096, obj_in: Categoria_4096Update) -> Categoria4096:
        """Actualizar categoria_4096"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar categoria_4096"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
categoria_4096_service = Categoria_4096Service()
