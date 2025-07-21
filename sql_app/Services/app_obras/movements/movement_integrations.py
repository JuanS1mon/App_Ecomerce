# Imports de terceros
from sqlalchemy.orm import Session
from datetime import datetime

# Imports del proyecto
from .service_movements import MovementService
from .schema_movements import MovementCreate
from .model_movements import MovementType, MovementStatus

def create_sale_movement(
    db: Session,
    artwork_id: int,
    sale_id: int,
    buyer_name: str = None,
    buyer_email: str = None,
    buyer_phone: str = None,
    to_location_id: int = None,
    notes: str = None
) -> int:
    """
    Crear automáticamente un movimiento cuando se realiza una venta
    
    Args:
        db: Sesión de base de datos
        artwork_id: ID de la obra vendida
        sale_id: ID de la venta
        buyer_name: Nombre del comprador
        buyer_email: Email del comprador  
        buyer_phone: Teléfono del comprador
        to_location_id: Ubicación de destino (opcional)
        notes: Notas adicionales
        
    Returns:
        ID del movimiento creado
    """
    service = MovementService(db)
    
    # Obtener la ubicación actual de la obra (si existe)
    current_movement = service.get_artwork_current_location(artwork_id)
    from_location_id = current_movement.to_location_id if current_movement else None
    
    # Finalizar movimiento anterior si está activo
    if current_movement and current_movement.status == MovementStatus.ACTIVO:
        service.finalize_movement(current_movement.id)
    
    # Crear el movimiento de venta
    movement_data = MovementCreate(
        artwork_id=artwork_id,
        movement_type=MovementType.VENTA,
        status=MovementStatus.ACTIVO,
        start_date=datetime.utcnow(),
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        contact_name=buyer_name,
        contact_email=buyer_email,
        contact_phone=buyer_phone,
        notes=notes or f"Venta automática - ID: {sale_id}",
        sale_id=sale_id
    )
    
    movement = service.create_movement(movement_data)
    return movement.id

def create_exhibition_movement(
    db: Session,
    artwork_id: int,
    exhibition_id: int,
    exhibition_location_id: int,
    contact_name: str = None,
    contact_email: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    notes: str = None
) -> int:
    """
    Crear automáticamente un movimiento cuando se agrega una obra a una exhibición
    
    Args:
        db: Sesión de base de datos
        artwork_id: ID de la obra
        exhibition_id: ID de la exhibición
        exhibition_location_id: Ubicación de la exhibición
        contact_name: Contacto de la exhibición
        contact_email: Email del contacto
        start_date: Fecha de inicio de la exhibición
        end_date: Fecha de finalización de la exhibición
        notes: Notas adicionales
        
    Returns:
        ID del movimiento creado
    """
    service = MovementService(db)
    
    # Obtener la ubicación actual de la obra
    current_movement = service.get_artwork_current_location(artwork_id)
    from_location_id = current_movement.to_location_id if current_movement else None
    
    # Crear el movimiento de exhibición
    movement_data = MovementCreate(
        artwork_id=artwork_id,
        movement_type=MovementType.EXHIBICION,
        status=MovementStatus.ACTIVO,
        start_date=start_date or datetime.utcnow(),
        end_date=end_date,
        from_location_id=from_location_id,
        to_location_id=exhibition_location_id,
        contact_name=contact_name,
        contact_email=contact_email,
        notes=notes or f"Exhibición automática - ID: {exhibition_id}",
        exhibition_id=exhibition_id
    )
    
    movement = service.create_movement(movement_data)
    return movement.id
