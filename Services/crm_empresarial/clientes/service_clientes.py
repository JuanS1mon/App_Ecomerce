# ============================================================================
# SERVICE: CLIENTES
# ============================================================================
"""
Service para clientes
Parte del servicio: crm_empresarial
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_clientes import Clientes
from .schema_clientes import ClientesCreate, ClientesUpdate

class ClientesService:
    """Service para operaciones CRUD de clientes"""
    
    def create(self, db: Session, obj_in: ClientesCreate) -> Clientes:
        """Crear nuevo registro de clientes"""
        obj_data = obj_in.model_dump()
        db_obj = Clientes(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Clientes]:
        """Obtener clientes por id"""
        return db.query(Clientes).filter(Clientes.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Clientes]:
        """Obtener múltiples registros de clientes"""
        return db.query(Clientes).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: Clientes, obj_in: ClientesUpdate) -> Clientes:
        """Actualizar clientes"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Eliminar clientes"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
clientes_service = ClientesService()
