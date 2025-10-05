# ============================================================================
# SERVICE: LIBROS
# ============================================================================
"""
Service para libros
Parte del servicio: biblioteca_sistema
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_libros import Libros
from .schema_libros import LibrosCreate, LibrosUpdate

class LibrosService:
    """Service para operaciones CRUD de libros"""
    
    def create(self, db: Session, obj_in: LibrosCreate) -> Libros:
        """Crear nuevo registro de libros"""
        obj_data = obj_in.model_dump()
        db_obj = Libros(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Libros]:
        """Obtener libros por id"""
        return db.query(Libros).filter(Libros.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Libros]:
        """Obtener múltiples registros de libros"""
        return db.query(Libros).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Libros, obj_in: LibrosUpdate) -> Libros:
        """Actualizar libros"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar libros"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
libros_service = LibrosService()
