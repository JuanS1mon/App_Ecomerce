# ============================================================================
# CRUD PARA TABLA: USUARIOS123
# ============================================================================
"""
Operaciones CRUD para usuarios123
Parte del servicio multi-tabla: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..sistema_visual_multiple_models import Usuarios123

class Usuarios123CRUD:
    """Operaciones CRUD para Usuarios123"""
    
    def create(self, db: Session, **kwargs) -> Usuarios123:
        """Crear nuevo registro de usuarios123"""
        db_obj = Usuarios123(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuarios123]:
        """Obtener usuarios123 por id"""
        return db.query(Usuarios123).filter(Usuarios123.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuarios123]:
        """Obtener todos los registros de usuarios123"""
        return db.query(Usuarios123).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[Usuarios123]:
        """Actualizar usuarios123"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuarios123"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
usuarios123_crud = Usuarios123CRUD()
