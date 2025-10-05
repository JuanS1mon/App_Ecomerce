# ============================================================================
# SERVICE: USUARIOS
# ============================================================================
"""
Service para usuarios
Parte del servicio: pizzeria_one_man_company
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuarios import Usuarios
from .schema_usuarios import UsuariosCreate, UsuariosUpdate

class UsuariosService:
    """Service para operaciones CRUD de usuarios"""
    
    def create(self, db: Session, obj_in: UsuariosCreate) -> Usuarios:
        """Crear nuevo registro de usuarios"""
        obj_data = obj_in.model_dump()
        db_obj = Usuarios(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuarios]:
        """Obtener usuarios por id"""
        return db.query(Usuarios).filter(Usuarios.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuarios]:
        """Obtener múltiples registros de usuarios"""
        return db.query(Usuarios).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Usuarios, obj_in: UsuariosUpdate) -> Usuarios:
        """Actualizar usuarios"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
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

# Instancia global del service
usuarios_service = UsuariosService()
