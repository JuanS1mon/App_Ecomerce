# ============================================================================
# TICKETS SERVICE - MAIN APPLICATION
# ============================================================================
# Servicio independiente para gestión de tickets y soporte

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# =============================
# MODELOS DE DATOS
# =============================
class Ticket(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    status: str = "abierto"  # abierto, en_progreso, resuelto, cerrado
    priority: str = "normal"  # baja, normal, alta, urgente
    category: str = "general"  # general, tecnico, funcional, bug
    created_by: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# =============================
# CONFIGURACIÓN DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tickets-service")

# =============================
# DATOS DEMO
# =============================
demo_tickets = [
    {
        "id": 1,
        "title": "Error en cálculo de stock",
        "description": "El sistema no calcula correctamente el stock disponible",
        "status": "abierto",
        "priority": "alta",
        "category": "bug",
        "created_by": "usuario1",
        "assigned_to": "dev_team",
        "created_at": "2025-08-20T10:30:00Z",
        "updated_at": "2025-08-20T10:30:00Z"
    },
    {
        "id": 2,
        "title": "Solicitud nueva funcionalidad - Reportes",
        "description": "Necesitamos reportes de inventario por fechas",
        "status": "en_progreso",
        "priority": "normal",
        "category": "funcional",
        "created_by": "admin",
        "assigned_to": "analysis_team",
        "created_at": "2025-08-19T14:15:00Z",
        "updated_at": "2025-08-22T09:45:00Z"
    },
    {
        "id": 3,
        "title": "Problema de performance en obras",
        "description": "Las consultas de proyectos tardan mucho en cargar",
        "status": "resuelto",
        "priority": "alta",
        "category": "tecnico",
        "created_by": "usuario2",
        "assigned_to": "dev_team",
        "created_at": "2025-08-18T16:20:00Z",
        "updated_at": "2025-08-23T11:30:00Z"
    }
]

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Tickets Service")
    logger.info("🎫 Módulos activos: tickets, support, notifications")
    yield
    # Shutdown
    logger.info("🛑 Cerrando Tickets Service")

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Tickets Service",
    description="Servicio independiente para gestión de tickets y soporte",
    version="1.0.0",
    docs_url="/tickets/docs",
    redoc_url="/tickets/redoc",
    lifespan=lifespan
)

# =============================
# CONFIGURACIÓN DE CORS
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# HEALTH CHECK
# =============================
@app.get("/tickets/health")
async def health_check():
    """Health check endpoint para el tickets service"""
    return {
        "status": "healthy",
        "service": "tickets-service",
        "version": "1.0.0",
        "features": {
            "ticket_management": "active",
            "support_system": "active",
            "notifications": "active",
            "reporting": "active"
        }
    }

# =============================
# TICKETS ENDPOINTS
# =============================
@app.get("/tickets")
async def get_tickets(status: Optional[str] = None, priority: Optional[str] = None):
    """Obtener lista de tickets"""
    tickets = demo_tickets
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]
    
    return {
        "tickets": tickets,
        "total": len(tickets),
        "filters": {"status": status, "priority": priority},
        "status": "success"
    }

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    """Obtener ticket específico"""
    ticket = next((t for t in demo_tickets if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return {
        "ticket": ticket,
        "status": "success"
    }

@app.post("/tickets")
async def create_ticket(ticket: Ticket):
    """Crear nuevo ticket"""
    new_id = max([t["id"] for t in demo_tickets]) + 1
    new_ticket = ticket.dict()
    new_ticket["id"] = new_id
    new_ticket["created_at"] = datetime.now().isoformat()
    new_ticket["updated_at"] = datetime.now().isoformat()
    demo_tickets.append(new_ticket)
    return {
        "ticket": new_ticket,
        "message": "Ticket creado exitosamente",
        "status": "success"
    }

# =============================
# DASHBOARD Y ESTADÍSTICAS
# =============================
@app.get("/tickets/dashboard")
async def get_dashboard():
    """Dashboard con estadísticas de tickets"""
    total_tickets = len(demo_tickets)
    open_tickets = len([t for t in demo_tickets if t["status"] == "abierto"])
    in_progress_tickets = len([t for t in demo_tickets if t["status"] == "en_progreso"])
    resolved_tickets = len([t for t in demo_tickets if t["status"] == "resuelto"])
    closed_tickets = len([t for t in demo_tickets if t["status"] == "cerrado"])
    
    high_priority = len([t for t in demo_tickets if t["priority"] == "alta"])
    urgent_priority = len([t for t in demo_tickets if t["priority"] == "urgente"])
    
    return {
        "summary": {
            "total": total_tickets,
            "open": open_tickets,
            "in_progress": in_progress_tickets,
            "resolved": resolved_tickets,
            "closed": closed_tickets
        },
        "priority": {
            "high": high_priority,
            "urgent": urgent_priority
        },
        "categories": {
            "bug": len([t for t in demo_tickets if t["category"] == "bug"]),
            "funcional": len([t for t in demo_tickets if t["category"] == "funcional"]),
            "tecnico": len([t for t in demo_tickets if t["category"] == "tecnico"])
        },
        "last_updated": datetime.now().isoformat(),
        "status": "success"
    }

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.get("/")
async def root():
    """Página principal del tickets service"""
    return {
        "message": "Tickets Service - Sistema de Soporte y Tickets",
        "version": "1.0.0",
        "docs": "/tickets/docs",
        "health": "/tickets/health",
        "dashboard": "/tickets/dashboard"
    }

# =============================
# MANEJADOR DE ERRORES
# =============================
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en Tickets Service: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in tickets service",
            "detail": str(exc),
            "service": "tickets-service"
        }
    )

# =============================
# EJECUCIÓN DEL SERVIDOR
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Tickets Service en puerto 8004")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=False
    )
