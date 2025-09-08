# ============================================================================
# SERVICE: USUARIO_4096
# ============================================================================
"""
Service para usuario_4096
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuario_4096 import Usuario4096
from .schema_usuario_4096 import Usuario_4096Create, Usuario_4096Update

class Usuario_4096Service:
    """Service para operaciones CRUD de usuario_4096"""
    
    def create(self, db: Session, obj_in: Usuario_4096Create) -> Usuario4096:
        """Crear nuevo registro de usuario_4096"""
        obj_data = obj_in.model_dump()
        db_obj = Usuario4096(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Usuario4096]:
        """Obtener usuario_4096 por id"""
        return db.query(Usuario4096).filter(Usuario4096.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario4096]:
        """Obtener múltiples registros de usuario_4096"""
        return db.query(Usuario4096).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Usuario4096, obj_in: Usuario_4096Update) -> Usuario4096:
        """Actualizar usuario_4096"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuario_4096"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
usuario_4096_service = Usuario_4096Service()
