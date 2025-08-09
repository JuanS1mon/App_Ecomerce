# ============================================================================
# SERVICE: OPORTUNIDADES
# ============================================================================
"""
Service para oportunidades
Parte del servicio: crm_empresarial
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_oportunidades import Oportunidades
from .schema_oportunidades import OportunidadesCreate, OportunidadesUpdate

class OportunidadesService:
    """Service para operaciones CRUD de oportunidades"""
    
    def create(self, db: Session, obj_in: OportunidadesCreate) -> Oportunidades:
        """Crear nuevo registro de oportunidades"""
        obj_data = obj_in.model_dump()
        db_obj = Oportunidades(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Oportunidades]:
        """Obtener oportunidades por id"""
        return db.query(Oportunidades).filter(Oportunidades.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Oportunidades]:
        """Obtener múltiples registros de oportunidades"""
        return db.query(Oportunidades).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Oportunidades, obj_in: OportunidadesUpdate) -> Oportunidades:
        """Actualizar oportunidades"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar oportunidades"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
oportunidades_service = OportunidadesService()
