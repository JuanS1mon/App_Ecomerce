# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

# Imports del proyecto
from .model_movements import Movements, MovementType, MovementStatus
from .model_contacts import Contacts
from .schema_movements import (
    MovementCreate, MovementUpdate, ContactCreate, ContactUpdate,
    GroupedMovementCreate
)

class MovementService:
    """Servicio para gestionar movimientos de obras de arte"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD básico para Movements
    def create_movement(self, movement_data: MovementCreate) -> Movements:
        """Crear un nuevo movimiento"""
        db_movement = Movements(**movement_data.dict())
        self.db.add(db_movement)
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement
    
    def create_grouped_movements(self, grouped_data: GroupedMovementCreate) -> List[Movements]:
        """Crear movimientos para múltiples obras"""
        movements = []
        for artwork_id in grouped_data.artwork_ids:
            movement_dict = grouped_data.dict()
            movement_dict.pop('artwork_ids')
            movement_dict['artwork_id'] = artwork_id
            
            db_movement = Movements(**movement_dict)
            self.db.add(db_movement)
            movements.append(db_movement)
        
        self.db.commit()
        for movement in movements:
            self.db.refresh(movement)
        return movements
    
    def get_movement(self, movement_id: int) -> Optional[Movements]:
        """Obtener un movimiento por ID"""
        return self.db.query(Movements).filter(Movements.id == movement_id).first()
    
    def get_movements(self, skip: int = 0, limit: int = 100) -> List[Movements]:
        """Obtener lista de movimientos con paginación"""
        return self.db.query(Movements).order_by(Movements.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_movements_by_artwork(self, artwork_id: int) -> List[Movements]:
        """Obtener todos los movimientos de una obra específica"""
        return self.db.query(Movements).filter(
            Movements.artwork_id == artwork_id
        ).order_by(Movements.created_at.desc()).all()
    
    def get_movements_by_location(self, location_id: int) -> List[Movements]:
        """Obtener movimientos por ubicación (origen o destino)"""
        return self.db.query(Movements).filter(
            or_(
                Movements.from_location_id == location_id,
                Movements.to_location_id == location_id
            )
        ).order_by(Movements.created_at.desc()).all()
    
    def get_active_movements(self) -> List[Movements]:
        """Obtener movimientos activos"""
        return self.db.query(Movements).filter(
            Movements.status == MovementStatus.ACTIVO
        ).order_by(Movements.created_at.desc()).all()
    
    def get_movements_by_type(self, movement_type: MovementType) -> List[Movements]:
        """Obtener movimientos por tipo"""
        return self.db.query(Movements).filter(
            Movements.movement_type == movement_type
        ).order_by(Movements.created_at.desc()).all()
    
    def update_movement(self, movement_id: int, movement_data: MovementUpdate) -> Optional[Movements]:
        """Actualizar un movimiento"""
        db_movement = self.get_movement(movement_id)
        if not db_movement:
            return None
        
        update_data = movement_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_movement, field, value)
        
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement
    
    def delete_movement(self, movement_id: int) -> bool:
        """Eliminar un movimiento"""
        db_movement = self.get_movement(movement_id)
        if not db_movement:
            return False
        
        self.db.delete(db_movement)
        self.db.commit()
        return True
    
    def get_artwork_current_location(self, artwork_id: int) -> Optional[Movements]:
        """Obtener la ubicación actual de una obra (último movimiento activo)"""
        return self.db.query(Movements).filter(
            and_(
                Movements.artwork_id == artwork_id,
                Movements.status == MovementStatus.ACTIVO
            )
        ).order_by(Movements.created_at.desc()).first()
    
    def finalize_movement(self, movement_id: int, end_date: Optional[datetime] = None) -> Optional[Movements]:
        """Finalizar un movimiento"""
        db_movement = self.get_movement(movement_id)
        if not db_movement:
            return None
        
        db_movement.status = MovementStatus.FINALIZADO
        db_movement.end_date = end_date or datetime.utcnow()
        db_movement.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement

class ContactService:
    """Servicio para gestionar contactos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_contact(self, contact_data: ContactCreate) -> Contacts:
        """Crear un nuevo contacto"""
        db_contact = Contacts(**contact_data.dict())
        self.db.add(db_contact)
        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact
    
    def get_contact(self, contact_id: int) -> Optional[Contacts]:
        """Obtener un contacto por ID"""
        return self.db.query(Contacts).filter(Contacts.id == contact_id).first()
    
    def get_contacts(self, skip: int = 0, limit: int = 100) -> List[Contacts]:
        """Obtener lista de contactos con paginación"""
        return self.db.query(Contacts).offset(skip).limit(limit).all()
    
    def search_contacts(self, search_term: str) -> List[Contacts]:
        """Buscar contactos por nombre, email o organización"""
        return self.db.query(Contacts).filter(
            or_(
                Contacts.name.contains(search_term),
                Contacts.email.contains(search_term),
                Contacts.organization.contains(search_term)
            )
        ).all()
    
    def update_contact(self, contact_id: int, contact_data: ContactUpdate) -> Optional[Contacts]:
        """Actualizar un contacto"""
        db_contact = self.get_contact(contact_id)
        if not db_contact:
            return None
        
        update_data = contact_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_contact, field, value)
        
        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact
    
    def delete_contact(self, contact_id: int) -> bool:
        """Eliminar un contacto"""
        db_contact = self.get_contact(contact_id)
        if not db_contact:
            return False
        
        self.db.delete(db_contact)
        self.db.commit()
        return True
