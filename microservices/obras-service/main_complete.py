# ============================================================================
# OBRAS SERVICE - MAIN APPLICATION (COMPLETE)
# ============================================================================
# Servicio independiente para la gestión de obras y proyectos

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
class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    status: str = "planificacion"  # planificacion, en_progreso, pausado, completado
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    client: Optional[str] = None

class Task(BaseModel):
    id: Optional[int] = None
    project_id: int
    name: str
    description: str
    status: str = "pendiente"  # pendiente, en_progreso, completado
    priority: str = "normal"  # baja, normal, alta, urgente
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = None

# =============================
# CONFIGURACIÓN DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("obras-service")

# =============================
# DATOS DEMO
# =============================
demo_projects = [
    {
        "id": 1,
        "name": "Construcción Edificio A",
        "description": "Proyecto de construcción de edificio residencial de 10 pisos",
        "status": "en_progreso",
        "start_date": "2025-01-15",
        "end_date": "2025-12-31",
        "budget": 2500000.00,
        "client": "Constructora ABC"
    },
    {
        "id": 2,
        "name": "Renovación Oficinas Central",
        "description": "Renovación completa de oficinas centrales",
        "status": "planificacion",
        "start_date": "2025-03-01",
        "end_date": "2025-06-30",
        "budget": 150000.00,
        "client": "Empresa XYZ"
    },
    {
        "id": 3,
        "name": "Puente Peatonal Norte",
        "description": "Construcción de puente peatonal en zona norte",
        "status": "completado",
        "start_date": "2024-08-01",
        "end_date": "2025-01-31",
        "budget": 75000.00,
        "client": "Municipalidad"
    }
]

demo_tasks = [
    {
        "id": 1,
        "project_id": 1,
        "name": "Excavación y cimientos",
        "description": "Excavación del terreno y construcción de cimientos",
        "status": "completado",
        "priority": "alta",
        "assigned_to": "Equipo A",
        "estimated_hours": 240
    },
    {
        "id": 2,
        "project_id": 1,
        "name": "Estructura principal",
        "description": "Construcción de la estructura principal del edificio",
        "status": "en_progreso",
        "priority": "alta",
        "assigned_to": "Equipo B",
        "estimated_hours": 480
    },
    {
        "id": 3,
        "project_id": 2,
        "name": "Diseño arquitectónico",
        "description": "Elaboración de planos y diseño de la renovación",
        "status": "pendiente",
        "priority": "normal",
        "assigned_to": "Arquitecto Principal",
        "estimated_hours": 80
    }
]

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Obras Service")
    logger.info("🏗️ Módulos activos: projects, tasks, resources, monitoring")
    yield
    # Shutdown
    logger.info("🛑 Cerrando Obras Service")

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Obras Service",
    description="Servicio independiente para gestión de obras y proyectos",
    version="1.0.0",
    docs_url="/obras/docs",
    redoc_url="/obras/redoc",
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
@app.get("/obras/health")
async def health_check():
    """Health check endpoint para el obras service"""
    return {
        "status": "healthy",
        "service": "obras-service",
        "version": "1.0.0",
        "features": {
            "project_management": "active",
            "task_tracking": "active",
            "resource_allocation": "active",
            "progress_monitoring": "active"
        }
    }

# =============================
# INFORMACIÓN DEL SERVICIO
# =============================
@app.get("/obras/info")
async def service_info():
    """Información detallada del obras service"""
    return {
        "name": "Obras Service",
        "description": "Servicio para gestión integral de obras y proyectos",
        "features": [
            {
                "name": "project_management",
                "description": "Gestión completa de proyectos",
                "endpoints": ["/obras/projects/*"]
            },
            {
                "name": "task_tracking",
                "description": "Seguimiento de tareas",
                "endpoints": ["/obras/tasks/*"]
            },
            {
                "name": "resource_allocation",
                "description": "Asignación de recursos",
                "endpoints": ["/obras/resources/*"]
            }
        ],
        "database": {
            "schema": "obras_db",
            "tables": ["projects", "tasks", "resources", "progress", "budgets"]
        }
    }

# =============================
# PROYECTOS ENDPOINTS
# =============================
@app.get("/obras/projects")
async def get_projects():
    """Obtener lista de proyectos"""
    return {
        "projects": demo_projects,
        "total": len(demo_projects),
        "status": "success"
    }

@app.get("/obras/projects/{project_id}")
async def get_project(project_id: int):
    """Obtener proyecto específico"""
    project = next((p for p in demo_projects if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {
        "project": project,
        "status": "success"
    }

@app.post("/obras/projects")
async def create_project(project: Project):
    """Crear nuevo proyecto"""
    new_id = max([p["id"] for p in demo_projects]) + 1
    new_project = project.dict()
    new_project["id"] = new_id
    demo_projects.append(new_project)
    return {
        "project": new_project,
        "message": "Proyecto creado exitosamente",
        "status": "success"
    }

# =============================
# TAREAS ENDPOINTS
# =============================
@app.get("/obras/tasks")
async def get_tasks(project_id: Optional[int] = None):
    """Obtener lista de tareas"""
    tasks = demo_tasks
    if project_id:
        tasks = [t for t in demo_tasks if t["project_id"] == project_id]
    return {
        "tasks": tasks,
        "total": len(tasks),
        "status": "success"
    }

@app.get("/obras/tasks/{task_id}")
async def get_task(task_id: int):
    """Obtener tarea específica"""
    task = next((t for t in demo_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {
        "task": task,
        "status": "success"
    }

@app.post("/obras/tasks")
async def create_task(task: Task):
    """Crear nueva tarea"""
    new_id = max([t["id"] for t in demo_tasks]) + 1
    new_task = task.dict()
    new_task["id"] = new_id
    demo_tasks.append(new_task)
    return {
        "task": new_task,
        "message": "Tarea creada exitosamente",
        "status": "success"
    }

# =============================
# DASHBOARD Y REPORTES
# =============================
@app.get("/obras/dashboard")
async def get_dashboard():
    """Dashboard con estadísticas generales"""
    total_projects = len(demo_projects)
    active_projects = len([p for p in demo_projects if p["status"] == "en_progreso"])
    completed_projects = len([p for p in demo_projects if p["status"] == "completado"])
    total_budget = sum([p.get("budget", 0) for p in demo_projects])
    
    total_tasks = len(demo_tasks)
    pending_tasks = len([t for t in demo_tasks if t["status"] == "pendiente"])
    in_progress_tasks = len([t for t in demo_tasks if t["status"] == "en_progreso"])
    completed_tasks = len([t for t in demo_tasks if t["status"] == "completado"])
    
    return {
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "completed": completed_projects,
            "budget_total": total_budget
        },
        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks
        },
        "last_updated": datetime.now().isoformat(),
        "status": "success"
    }

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.get("/")
async def root():
    """Página principal del obras service"""
    return {
        "message": "Obras Service - Gestión de Proyectos y Obras",
        "version": "1.0.0",
        "docs": "/obras/docs",
        "health": "/obras/health",
        "info": "/obras/info",
        "dashboard": "/obras/dashboard"
    }

# =============================
# API DE COMUNICACIÓN CON CORE
# =============================
@app.get("/obras/auth/verify")
async def verify_with_core():
    """Endpoint para verificar autenticación con el core service"""
    return {
        "message": "Authentication verification with core service",
        "core_service_url": "http://localhost:8001/core/health",
        "status": "simulation"
    }

# =============================
# MANEJADOR DE ERRORES
# =============================
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en Obras Service: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in obras service",
            "detail": str(exc),
            "service": "obras-service"
        }
    )

# =============================
# EJECUCIÓN DEL SERVIDOR
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Obras Service en puerto 8003")
    uvicorn.run(
        "main_complete:app",
        host="0.0.0.0",
        port=8003,
        reload=False
    )
