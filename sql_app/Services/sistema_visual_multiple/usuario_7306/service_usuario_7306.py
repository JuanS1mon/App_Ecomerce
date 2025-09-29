# ============================================================================
# SERVICE: USUARIO_7306
# ============================================================================
"""
Service para usuario_7306
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuario_7306 import Usuario7306
from .schema_usuario_7306 import Usuario_7306Create, Usuario_7306Update

class Usuario_7306Service:
    """Service para operaciones CRUD de usuario_7306"""
    
    def create(self, db: Session, obj_in: Usuario_7306Create) -> Usuario7306:
        """Crear nuevo registro de usuario_7306"""
        obj_data = obj_in.model_dump()
        db_obj = Usuario7306(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuario7306]:
        """Obtener usuario_7306 por id"""
        return db.query(Usuario7306).filter(Usuario7306.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario7306]:
        """Obtener múltiples registros de usuario_7306"""
        return db.query(Usuario7306).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Usuario7306, obj_in: Usuario_7306Update) -> Usuario7306:
        """Actualizar usuario_7306"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuario_7306"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
usuario_7306_service = Usuario_7306Service()
