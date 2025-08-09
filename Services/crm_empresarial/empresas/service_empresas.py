# ============================================================================
# SERVICE: EMPRESAS
# ============================================================================
"""
Service para empresas
Parte del servicio: crm_empresarial
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_empresas import Empresas
from .schema_empresas import EmpresasCreate, EmpresasUpdate

class EmpresasService:
    """Service para operaciones CRUD de empresas"""
    
    def create(self, db: Session, obj_in: EmpresasCreate) -> Empresas:
        """Crear nuevo registro de empresas"""
        obj_data = obj_in.model_dump()
        db_obj = Empresas(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Empresas]:
        """Obtener empresas por id"""
        return db.query(Empresas).filter(Empresas.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Empresas]:
        """Obtener múltiples registros de empresas"""
        return db.query(Empresas).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Empresas, obj_in: EmpresasUpdate) -> Empresas:
        """Actualizar empresas"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar empresas"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
empresas_service = EmpresasService()
