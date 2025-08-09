# ============================================================================
# SERVICE: CONTACTOS
# ============================================================================
"""
Service para contactos
Parte del servicio: crm_empresarial
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_contactos import Contactos
from .schema_contactos import ContactosCreate, ContactosUpdate

class ContactosService:
    """Service para operaciones CRUD de contactos"""
    
    def create(self, db: Session, obj_in: ContactosCreate) -> Contactos:
        """Crear nuevo registro de contactos"""
        obj_data = obj_in.model_dump()
        db_obj = Contactos(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Contactos]:
        """Obtener contactos por id"""
        return db.query(Contactos).filter(Contactos.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Contactos]:
        """Obtener múltiples registros de contactos"""
        return db.query(Contactos).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Contactos, obj_in: ContactosUpdate) -> Contactos:
        """Actualizar contactos"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar contactos"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
contactos_service = ContactosService()
