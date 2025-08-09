# ============================================================================
# CRUD PARA TABLA: USUARIOS
# ============================================================================
"""
Operaciones CRUD para usuarios
Parte del servicio multi-tabla: ecommerce_app
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..ecommerce_app_models import Usuarios

class UsuariosCRUD:
    """Operaciones CRUD para Usuarios"""
    
    def create(self, db: Session, **kwargs) -> Usuarios:
        """Crear nuevo registro de usuarios"""
        db_obj = Usuarios(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuarios]:
        """Obtener usuarios por id"""
        return db.query(Usuarios).filter(Usuarios.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuarios]:
        """Obtener todos los registros de usuarios"""
        return db.query(Usuarios).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[Usuarios]:
        """Actualizar usuarios"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuarios"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global
usuarios_crud = UsuariosCRUD()
