# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Imports del proyecto
from ....db.database import get_db
from .service_movements import MovementService, ContactService
from .schema_movements import (
    MovementCreate, MovementUpdate, MovementResponse,
    ContactCreate, ContactUpdate, ContactResponse,
    GroupedMovementCreate, MovementHistoryResponse
)
from .model_movements import MovementType, MovementStatus

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/movements",
    tags=["movements"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# ============================================================================
# RUTAS PARA MOVEMENTS
# ============================================================================

@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def routes_post_movements(movement: MovementCreate, db: Session = Depends(get_db)):
    """Crear un nuevo movimiento de obra"""
    if not movement.artwork_id or not movement.movement_type:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos artwork_id y movement_type son obligatorios")
    try:
        service = MovementService(db)
        return service.create_movement(movement)
    except Exception as e:
        logger.error(f"Error al crear movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el movimiento.")

@router.post("/traslado", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def routes_post_traslado(movement: MovementCreate, db: Session = Depends(get_db)):
    """Crear un nuevo traslado de obra entre ubicaciones"""
    # Validar que sea un traslado
    if movement.movement_type != MovementType.TRASLADO:
        movement.movement_type = MovementType.TRASLADO
    
    if not movement.artwork_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El campo artwork_id es obligatorio")
    
    if not movement.from_location_id or not movement.to_location_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Los campos from_location_id y to_location_id son obligatorios para traslados")
    
    if movement.from_location_id == movement.to_location_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La ubicación de origen y destino no pueden ser la misma")
    
    try:
        service = MovementService(db)
        return service.create_movement(movement)
    except Exception as e:
        logger.error(f"Error al crear traslado: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el traslado.")

@router.post("/grouped", response_model=List[MovementResponse], status_code=status.HTTP_201_CREATED)
async def routes_post_grouped_movements(grouped_movement: GroupedMovementCreate, db: Session = Depends(get_db)):
    """Crear movimientos para múltiples obras"""
    try:
        service = MovementService(db)
        return service.create_grouped_movements(grouped_movement)
    except Exception as e:
        logger.error(f"Error al crear movimientos agrupados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear los movimientos.")

@router.get("/", response_model=List[MovementResponse])
async def routes_get_all_movements(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000),
    movement_type: Optional[MovementType] = Query(None),
    status_filter: Optional[MovementStatus] = Query(None, alias="status"),
    artwork_id: Optional[int] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de movimientos con filtros opcionales"""
    try:
        service = MovementService(db)
        
        if artwork_id:
            movements = service.get_movements_by_artwork(artwork_id)
        elif location_id:
            movements = service.get_movements_by_location(location_id)
        elif movement_type:
            movements = service.get_movements_by_type(movement_type)
        elif status_filter == MovementStatus.ACTIVO:
            movements = service.get_active_movements()
        else:
            movements = service.get_movements(skip, limit)
        
        return movements
    except Exception as e:
        logger.error(f"Error al obtener movimientos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

# Estas rutas se han movido al final del archivo con el patrón /{id} estándar

# ============================================================================
# RUTAS PARA HISTORIAL Y UBICACIÓN ACTUAL
# ============================================================================

@router.get("/artworks/{artwork_id}/movements", response_model=List[MovementResponse])
async def routes_get_artwork_movements(artwork_id: int, db: Session = Depends(get_db)):
    """Obtener historial completo de movimientos de una obra"""
    try:
        service = MovementService(db)
        return service.get_movements_by_artwork(artwork_id)
    except Exception as e:
        logger.error(f"Error al obtener movimientos de obra: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los movimientos.")

@router.get("/artworks/{artwork_id}/current-location", response_model=Optional[MovementResponse])
async def routes_get_artwork_current_location(artwork_id: int, db: Session = Depends(get_db)):
    """Obtener la ubicación actual de una obra"""
    try:
        service = MovementService(db)
        return service.get_artwork_current_location(artwork_id)
    except Exception as e:
        logger.error(f"Error al obtener ubicación actual: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la ubicación.")

@router.get("/dashboard/active", response_model=List[MovementResponse])
async def routes_get_active_movements_dashboard(db: Session = Depends(get_db)):
    """Dashboard de movimientos activos"""
    try:
        service = MovementService(db)
        return service.get_active_movements()
    except Exception as e:
        logger.error(f"Error al obtener movimientos activos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los movimientos activos.")

@router.get("/dashboard/stats")
async def routes_get_movement_stats(db: Session = Depends(get_db)):
    """Estadísticas para el dashboard"""
    try:
        service = MovementService(db)
        active_movements = service.get_active_movements()
        prestamos = [m for m in active_movements if m.movement_type == MovementType.PRESTAMO]
        traslados = [m for m in active_movements if m.movement_type == MovementType.TRASLADO]
        
        return {
            "total_active": len(active_movements),
            "prestamos": len(prestamos),
            "traslados": len(traslados),
            "exhibiciones": len([m for m in active_movements if m.movement_type == MovementType.EXHIBICION]),
            "ventas": len([m for m in active_movements if m.movement_type == MovementType.VENTA])
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las estadísticas.")

# ============================================================================
# RUTAS PARA CONTACTOS
# ============================================================================

@router.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Crear un nuevo contacto"""
    try:
        service = ContactService(db)
        return service.create_contact(contact)
    except Exception as e:
        logger.error(f"Error al crear contacto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el contacto.")

@router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    contact_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de contactos con filtros opcionales"""
    try:
        service = ContactService(db)
        return service.get_contacts(skip, limit, search, contact_type)
    except Exception as e:
        logger.error(f"Error al obtener contactos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista de contactos.")

@router.get("/contacts/count")
async def get_contacts_count(
    search: Optional[str] = Query(None),
    contact_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener conteo de contactos"""
    try:
        service = ContactService(db)
        contacts = service.get_contacts(0, 10000, search, contact_type)
        return {"total": len(contacts)}
    except Exception as e:
        logger.error(f"Error al contar contactos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al contar contactos.")

@router.get("/contacts/stats")
async def get_contacts_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de contactos"""
    try:
        service = ContactService(db)
        contacts = service.get_contacts(0, 10000)
        
        total = len(contacts)
        institutions = len([c for c in contacts if c.contact_type == "INSTITUTION"])
        individuals = len([c for c in contacts if c.contact_type == "INDIVIDUAL"])
        
        # Contactos con movimientos (esto requeriría una consulta más compleja)
        with_movements = 0  # Por ahora 0, se puede implementar más tarde
        
        return {
            "total": total,
            "institutions": institutions,
            "individuals": individuals,
            "withMovements": with_movements
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de contactos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener estadísticas.")

@router.get("/contacts/id/{id}", response_model=ContactResponse)
async def get_contact(id: int, db: Session = Depends(get_db)):
    """Obtener un contacto específico"""
    try:
        service = ContactService(db)
        contact = service.get_contact(id)
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
        return contact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener contacto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el contacto.")

@router.put("/contacts/id/{id}", response_model=ContactResponse)
async def update_contact(id: int, contact_data: ContactUpdate, db: Session = Depends(get_db)):
    """Actualizar un contacto"""
    try:
        service = ContactService(db)
        contact = service.update_contact(id, contact_data)
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
        return contact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar contacto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el contacto.")

@router.delete("/contacts/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(id: int, db: Session = Depends(get_db)):
    """Eliminar un contacto"""
    try:
        service = ContactService(db)
        success = service.delete_contact(id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar contacto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el contacto.")

# ============================================================================
# RUTAS HTML PARA CONTACTOS
# ============================================================================

@router.get("/contacts/html/", response_class=HTMLResponse)
async def get_contacts_list_html(request: Request, db: Session = Depends(get_db)):
    """Página de listado de contactos"""
    try:
        return templates.TemplateResponse("app_obras/movements/contacts/list.html", {
            "request": request
        })
    except Exception as e:
        logger.error(f"Error al cargar página de contactos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/contacts/html/create", response_class=HTMLResponse) 
async def get_contacts_create_html(request: Request, db: Session = Depends(get_db)):
    """Página de creación de contacto"""
    try:
        return templates.TemplateResponse("app_obras/movements/contacts/create.html", {
            "request": request
        })
    except Exception as e:
        logger.error(f"Error al cargar página de creación de contacto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/contacts/html/edit", response_class=HTMLResponse)
async def get_contacts_edit_html(request: Request, id: int = Query(...), db: Session = Depends(get_db)):
    """Página de edición de contacto"""
    try:
        service = ContactService(db)
        contact = service.get_contact(id)
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
        
        return templates.TemplateResponse("app_obras/movements/contacts/edit.html", {
            "request": request,
            "contact": contact
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición de contacto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

# ============================================================================
# RUTAS HTML PARA MOVIMIENTOS
# ============================================================================

@router.get("/test-debug", response_class=HTMLResponse)
async def test_debug():
    logger.info("🔍 TEST DEBUG - Endpoint alcanzado")
    return HTMLResponse(content="<h1>Test Debug OK</h1>")

# RUTA DE PRUEBA ESPECÍFICA PARA TRASLADO
@router.get("/test-traslado", response_class=HTMLResponse)
async def test_traslado():
    logger.info("🔍 TEST TRASLADO - Endpoint alcanzado")
    return HTMLResponse(content="<h1>Test Traslado OK</h1>")

# RUTA SUPER ESPECÍFICA PARA DEBUG ABSOLUTO
@router.get("/super-test-unico-12345", response_class=HTMLResponse)
async def super_test_unico():
    logger.info("🔍 SUPER TEST - Endpoint alcanzado")
    return HTMLResponse(content="<h1>Super Test Unico OK</h1>")

@router.get("/html/", response_class=HTMLResponse)
async def get_movements_html(request: Request, db: Session = Depends(get_db)):
    """Página principal de movimientos con lista y opciones de traslado"""
    try:
        logger.info("🔍 Cargando página de movimientos")
        service = MovementService(db)
        movements = service.get_movements(0, 1000)  # Obtener todos los movimientos
        logger.info(f"✅ Movimientos obtenidos: {len(movements) if movements else 0}")
        
        # Cargar datos adicionales para el template
        from ..locations.service_locations import get_all_locations
        locations = get_all_locations(db, 0, 1000)
        logger.info(f"✅ Ubicaciones obtenidas: {len(locations) if locations else 0}")
        
        from datetime import datetime
        current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
        current_month = datetime.now().replace(day=1)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return templates.TemplateResponse("templates/movements/list.html", {
            "request": request,
            "movements": movements,
            "locations": locations,
            "current_datetime": current_datetime,
            "current_month": current_month,
            "today": today
        })
    except Exception as e:
        logger.error(f"❌ Error al cargar página de movimientos: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
        # Retornar una página de error simple
        return HTMLResponse(content=f"""
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error al cargar movimientos</h1>
            <p>Error: {str(e)}</p>
            <a href="/obras_dashboard.html">Volver al Dashboard</a>
        </body>
        </html>
        """, status_code=500)

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_movements_html(request: Request, db: Session = Depends(get_db)):
    """Página de creación de movimiento con datos de obras y ubicaciones"""
    try:
        # Cargar datos necesarios para los selects
        from ..artworks.service_artworks import get_all_artworks
        from ..locations.service_locations import get_all_locations
        
        artworks = get_all_artworks(db, 0, 1000)
        locations = get_all_locations(db, 0, 1000)
        
        return templates.TemplateResponse("app_obras/movements/create.html", {
            "request": request,
            "artworks": artworks,
            "locations": locations
        })
    except Exception as e:
        logger.error(f"Error al cargar página de creación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/traslado", response_class=HTMLResponse)
async def get_create_traslado_html(request: Request, db: Session = Depends(get_db)):
    """Página específica para crear traslados de obras entre ubicaciones"""
    try:
        # Cargar datos necesarios para los selects
        from ..artworks.service_artworks import get_all_artworks
        from ..locations.service_locations import get_all_locations
        
        artworks = get_all_artworks(db, 0, 1000)
        locations = get_all_locations(db, 0, 1000)
        
        return templates.TemplateResponse("templates/movements/traslado.html", {
            "request": request,
            "artworks": artworks,
            "locations": locations
        })
    except Exception as e:
        logger.error(f"Error al cargar página de traslado: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/edit", response_class=HTMLResponse)
async def get_edit_movements_html_with_id(request: Request, id: int = Query(...), db: Session = Depends(get_db)):
    """Página de edición de movimiento con datos precargados"""
    try:
        service = MovementService(db)
        movement = service.get_movement(id)
        if not movement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
        
        # Cargar datos para los selects
        from ..artworks.service_artworks import get_all_artworks
        from ..locations.service_locations import get_all_locations
        
        artworks = get_all_artworks(db, 0, 1000)
        locations = get_all_locations(db, 0, 1000)
        
        return templates.TemplateResponse("app_obras/movements/edit.html", {
            "request": request,
            "movement": movement,
            "artworks": artworks,
            "locations": locations
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/dashboard", response_class=HTMLResponse)
async def get_movements_dashboard_html(request: Request, db: Session = Depends(get_db)):
    try:
        service = MovementService(db)
        active_movements = service.get_active_movements()
        return templates.TemplateResponse("app_obras/movements/dashboard.html", {
            "request": request,
            "active_movements": active_movements
        })
    except Exception as e:
        logger.error(f"Error al cargar dashboard de movimientos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/history", response_class=HTMLResponse)
async def get_movements_history_html(request: Request, db: Session = Depends(get_db)):
    try:
        service = MovementService(db)
        movements = service.get_movements(0, 1000)  # Obtener historial completo
        return templates.TemplateResponse("app_obras/movements/history.html", {
            "request": request,
            "movements": movements
        })
    except Exception as e:
        logger.error(f"Error al cargar historial de movimientos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

# ============================================================================
# ROUTER API para integración con dashboard principal
# ============================================================================

api_router = APIRouter(
    prefix="/api/v1/movements",
    tags=["movements-api"]
)

@api_router.get("/dashboard/stats")
async def api_get_movement_stats(db: Session = Depends(get_db)):
    """API de estadísticas para el dashboard principal"""
    try:
        service = MovementService(db)
        active_movements = service.get_active_movements()
        prestamos = [m for m in active_movements if m.movement_type == MovementType.PRESTAMO]
        traslados = [m for m in active_movements if m.movement_type == MovementType.TRASLADO]
        
        return {
            "total_active": len(active_movements),
            "prestamos": len(prestamos),
            "traslados": len(traslados),
            "exhibiciones": len([m for m in active_movements if m.movement_type == MovementType.EXHIBICION]),
            "ventas": len([m for m in active_movements if m.movement_type == MovementType.VENTA])
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las estadísticas.")

# ============================================================================
# RUTAS ADICIONALES Y ESTADÍSTICAS
# ============================================================================

@router.get("/stats")
async def get_movements_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de movimientos para el dashboard"""
    try:
        service = MovementService(db)
        movements = service.get_movements(0, 10000)  # Obtener todos para estadísticas
        
        # Calcular estadísticas
        total = len(movements)
        active = len([m for m in movements if m.status == MovementStatus.ACTIVO])
        finished = len([m for m in movements if m.status == MovementStatus.FINALIZADO])
        
        # Por tipo
        by_type = {}
        for movement_type in MovementType:
            by_type[movement_type.value] = len([m for m in movements if m.movement_type == movement_type])
        
        # Este mes
        from datetime import datetime, timedelta
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = len([m for m in movements if m.created_at and m.created_at >= current_month])
        
        # Por mes (últimos 6 meses)
        by_month = {}
        for i in range(6):
            month_start = current_month - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            month_name = month_start.strftime("%b %Y")
            count = len([m for m in movements if m.created_at and month_start <= m.created_at < month_end])
            by_month[month_name] = count
        
        return {
            "total": total,
            "active": active,
            "finished": finished,
            "thisMonth": this_month,
            "byType": by_type,
            "byMonth": by_month
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener estadísticas.")

@router.get("/location-stats")
async def get_location_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas por ubicación"""
    try:
        service = MovementService(db)
        return service.get_location_statistics()
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de ubicación: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener estadísticas de ubicación.")

@router.get("/count")
async def get_movements_count(
    movement_type: Optional[MovementType] = Query(None),
    status_filter: Optional[MovementStatus] = Query(None, alias="status"),
    artwork_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener conteo de movimientos con filtros"""
    try:
        service = MovementService(db)
        # Aplicar los mismos filtros que en la lista
        if artwork_id:
            movements = service.get_movements_by_artwork(artwork_id)
        elif movement_type:
            movements = service.get_movements_by_type(movement_type)
        elif status_filter == MovementStatus.ACTIVO:
            movements = service.get_active_movements()
        else:
            movements = service.get_movements(0, 10000)  # Obtener todos para contar
        
        return {"total": len(movements)}
    except Exception as e:
        logger.error(f"Error al contar movimientos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al contar movimientos.")

# ============================================================================
# RUTAS GENÉRICAS CON PARÁMETROS (VAN AL FINAL PARA NO INTERFERIR)
# ============================================================================

# Corregir rutas con parámetros de path siguiendo el patrón de artists
@router.get("/id/{id}", response_model=MovementResponse)
async def routes_get_movements_by_id(id: int, db: Session = Depends(get_db)):
    """Obtener un movimiento específico"""
    try:
        service = MovementService(db)
        movement = service.get_movement(id)
        if not movement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
        return movement
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el movimiento.")

@router.put("/id/{id}", response_model=MovementResponse)
async def routes_update_movements_by_id(id: int, movement_data: MovementUpdate, db: Session = Depends(get_db)):
    """Actualizar un movimiento"""
    try:
        service = MovementService(db)
        movement = service.update_movement(id, movement_data)
        if not movement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
        return movement
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el movimiento.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_movements_by_id(id: int, db: Session = Depends(get_db)):
    """Eliminar un movimiento"""
    try:
        service = MovementService(db)
        success = service.delete_movement(id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el movimiento.")

@router.put("/id/{id}/finalize", response_model=MovementResponse)
async def routes_finalize_movement_by_id(id: int, db: Session = Depends(get_db)):
    """Finalizar un movimiento"""
    try:
        service = MovementService(db)
        movement = service.finalize_movement(id)
        if not movement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
        return movement
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al finalizar movimiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al finalizar el movimiento.")


