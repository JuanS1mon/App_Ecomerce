# ============================================================================
# SERVICE: USUARIO_5372
# ============================================================================
"""
Service para usuario_5372
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuario_5372 import Usuario5372
from .schema_usuario_5372 import Usuario_5372Create, Usuario_5372Update

class Usuario_5372Service:
    """Service para operaciones CRUD de usuario_5372"""
    
    def create(self, db: Session, obj_in: Usuario_5372Create) -> Usuario5372:
        """Crear nuevo registro de usuario_5372"""
        obj_data = obj_in.model_dump()
        db_obj = Usuario5372(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuario5372]:
        """Obtener usuario_5372 por id"""
        return db.query(Usuario5372).filter(Usuario5372.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario5372]:
        """Obtener múltiples registros de usuario_5372"""
        return db.query(Usuario5372).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Usuario5372, obj_in: Usuario_5372Update) -> Usuario5372:
        """Actualizar usuario_5372"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuario_5372"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
usuario_5372_service = Usuario_5372Service()
