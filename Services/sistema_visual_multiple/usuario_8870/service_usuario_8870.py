# ============================================================================
# SERVICE: USUARIO_8870
# ============================================================================
"""
Service para usuario_8870
Parte del servicio: sistema_visual_multiple
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_usuario_8870 import Usuario8870
from .schema_usuario_8870 import Usuario8870Create, Usuario8870Update

class Usuario8870Service:
    """Service para operaciones CRUD de usuario_8870"""

    def create(self, db: Session, obj_in: Usuario8870Create) -> Usuario8870:
        """Crear nuevo registro de usuario_8870"""
        db_obj = Usuario8870(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[Usuario8870]:
        """Obtener usuario_8870 por id"""
        return db.query(Usuario8870).filter(Usuario8870.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario8870]:
        """Obtener múltiples registros de usuario_8870"""
        return db.query(Usuario8870).offset(skip).limit(limit).all()

    def update(self, db: Session, db_obj: Usuario8870, obj_in: Usuario8870Update) -> Usuario8870:
        """Actualizar usuario_8870"""
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """Eliminar usuario_8870"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
usuario_8870_service = Usuario8870Service()
