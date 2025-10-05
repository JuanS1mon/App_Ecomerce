# ============================================================================
# SERVICE: USUARIO_5862
# ============================================================================
"""
Service para usuario_5862
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuario_5862 import Usuario5862
from .schema_usuario_5862 import Usuario_5862Create, Usuario_5862Update

class Usuario_5862Service:
    """Service para operaciones CRUD de usuario_5862"""
    
    def create(self, db: Session, obj_in: Usuario_5862Create) -> Usuario5862:
        """Crear nuevo registro de usuario_5862"""
        obj_data = obj_in.model_dump()
        db_obj = Usuario5862(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuario5862]:
        """Obtener usuario_5862 por id"""
        return db.query(Usuario5862).filter(Usuario5862.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario5862]:
        """Obtener múltiples registros de usuario_5862"""
        return db.query(Usuario5862).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Usuario5862, obj_in: Usuario_5862Update) -> Usuario5862:
        """Actualizar usuario_5862"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuario_5862"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
usuario_5862_service = Usuario_5862Service()
