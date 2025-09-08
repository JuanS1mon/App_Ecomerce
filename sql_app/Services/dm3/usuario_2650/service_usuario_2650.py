# ============================================================================
# SERVICE: USUARIO_2650
# ============================================================================
"""
Service para usuario_2650
Parte del servicio: dm3
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuario_2650 import Usuario2650
from .schema_usuario_2650 import Usuario_2650Create, Usuario_2650Update

class Usuario_2650Service:
    """Service para operaciones CRUD de usuario_2650"""
    
    def create(self, db: Session, obj_in: Usuario_2650Create) -> Usuario2650:
        """Crear nuevo registro de usuario_2650"""
        obj_data = obj_in.model_dump()
        db_obj = Usuario2650(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuario2650]:
        """Obtener usuario_2650 por id"""
        return db.query(Usuario2650).filter(Usuario2650.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario2650]:
        """Obtener múltiples registros de usuario_2650"""
        return db.query(Usuario2650).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Usuario2650, obj_in: Usuario_2650Update) -> Usuario2650:
        """Actualizar usuario_2650"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuario_2650"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
usuario_2650_service = Usuario_2650Service()
