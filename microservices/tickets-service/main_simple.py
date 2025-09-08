"""
Tickets Service - Sistema de Soporte y Tickets
Servicio independiente para gestión de tickets y soporte técnico
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

# Configurar logging simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tickets-service")

# Modelos Pydantic
class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    category: str = "general"
    user_id: str

class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: str = "open"
    priority: str = "medium"
    category: str = "general"
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Base de datos en memoria (demo)
tickets_db = []
ticket_counter = 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida del servicio"""
    logger.info("🚀 Iniciando Tickets Service")
    logger.info("🎫 Módulos activos: tickets, support, notifications")
    
    # Datos de demostración
    global tickets_db, ticket_counter
    demo_tickets = [
        {"id": 1, "title": "Problema de conexión", "description": "No puedo conectar", 
         "status": "open", "priority": "high", "category": "technical", "user_id": "user1",
         "created_at": datetime.now()},
        {"id": 2, "title": "Solicitud de funcionalidad", "description": "Nueva característica", 
         "status": "in_progress", "priority": "medium", "category": "feature", "user_id": "user2",
         "created_at": datetime.now()},
    ]
    tickets_db.extend(demo_tickets)
    ticket_counter = 3
    
    yield
    
    logger.info("🛑 Cerrando Tickets Service")

# Crear aplicación FastAPI
app = FastAPI(
    title="Tickets Service",
    description="Servicio de gestión de tickets y soporte técnico",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tickets/health")
async def health_check():
    """Verificación de salud del servicio"""
    return {
        "status": "healthy",
        "service": "tickets-service",
        "version": "1.0.0",
        "features": {
            "ticket_management": "active",
            "support_tracking": "active",
            "notification_system": "active",
            "analytics": "active"
        }
    }

@app.get("/tickets/")
async def get_tickets():
    """Obtener todos los tickets"""
    return {"tickets": tickets_db, "total": len(tickets_db)}

@app.post("/tickets/", response_model=Ticket)
async def create_ticket(ticket: TicketCreate):
    """Crear un nuevo ticket"""
    global ticket_counter
    
    new_ticket = {
        "id": ticket_counter,
        "title": ticket.title,
        "description": ticket.description,
        "status": "open",
        "priority": ticket.priority,
        "category": ticket.category,
        "user_id": ticket.user_id,
        "created_at": datetime.now(),
        "updated_at": None
    }
    
    tickets_db.append(new_ticket)
    ticket_counter += 1
    
    logger.info(f"🎫 Nuevo ticket creado: {new_ticket['id']} - {new_ticket['title']}")
    return new_ticket

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    """Obtener un ticket específico"""
    ticket = next((t for t in tickets_db if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket

@app.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: int, status: str):
    """Actualizar estado de un ticket"""
    ticket = next((t for t in tickets_db if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    ticket["status"] = status
    ticket["updated_at"] = datetime.now()
    
    logger.info(f"🔄 Ticket {ticket_id} actualizado: {status}")
    return ticket

@app.get("/tickets/stats/dashboard")
async def get_dashboard():
    """Dashboard con estadísticas de tickets"""
    total_tickets = len(tickets_db)
    open_tickets = len([t for t in tickets_db if t["status"] == "open"])
    closed_tickets = len([t for t in tickets_db if t["status"] == "closed"])
    in_progress = len([t for t in tickets_db if t["status"] == "in_progress"])
    
    by_priority = {}
    by_category = {}
    
    for ticket in tickets_db:
        priority = ticket.get("priority", "unknown")
        category = ticket.get("category", "unknown")
        
        by_priority[priority] = by_priority.get(priority, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
    
    return {
        "summary": {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "closed_tickets": closed_tickets,
            "in_progress": in_progress
        },
        "by_priority": by_priority,
        "by_category": by_category,
        "recent_tickets": tickets_db[-5:] if tickets_db else []
    }

@app.get("/tickets/search")
async def search_tickets(status: Optional[str] = None, priority: Optional[str] = None, category: Optional[str] = None):
    """Buscar tickets por filtros"""
    filtered_tickets = tickets_db
    
    if status:
        filtered_tickets = [t for t in filtered_tickets if t["status"] == status]
    if priority:
        filtered_tickets = [t for t in filtered_tickets if t["priority"] == priority]
    if category:
        filtered_tickets = [t for t in filtered_tickets if t["category"] == category]
    
    return {
        "tickets": filtered_tickets,
        "total": len(filtered_tickets),
        "filters": {"status": status, "priority": priority, "category": category}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
