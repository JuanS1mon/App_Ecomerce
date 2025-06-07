import os
import re
from fastapi import FastAPI, Form, Request, APIRouter, status, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session
from ...Services.security.security import encriptar_clave, get_current_user  # Importar la función de seguridad
from ...db.database import get_db
from ...db.models.config.usuarios import usuarios 
from ...db.models.config.activityLog import ActivityLog
from datetime import date, timedelta
from ...db.schemas.config.Usuarios import UserDB  # Asegúrate de importar UserDB

templates = Jinja2Templates(directory="sql_app/static")  # Cambiado para coincidir con main.py

def create_admin_router(app: FastAPI):
    router = APIRouter(
        include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
        prefix="/admin",
        tags=["Admin"],
        responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
    )
    @router.get("")
    async def admin_page(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
        # Verificar si el usuario es admin
        is_admin = False
        
        if isinstance(current_user, dict):
            # Si es un diccionario, verificamos en los roles (adaptado a la estructura de tu dict)
            if "roles" in current_user:
                is_admin = any(role["nombre"] == "admin" for role in current_user["roles"])
        else:
            # Si es un objeto UserDB
            if hasattr(current_user, "roles"):
                is_admin = any(role.nombre == "admin" for role in current_user.roles)
        
        # Si no es admin, denegar acceso
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requiere rol de administrador para acceder a esta página",
                headers={"Location": "/unauthorized"}
            )
        
        # Obtener estadísticas
        user_count = db.query(usuarios).count()
        
        # Obtener actividades usando SQL nativo para evitar errores de ORM
        activity_query = text("""
            SELECT a.id, a.action, a.timestamp, u.usuario, u.nombre
            FROM activity_log a
            LEFT JOIN Usuarios u ON a.user_id = u.codigo
            ORDER BY a.timestamp DESC
        """)
        
        activities_raw = db.execute(activity_query).fetchall()
        
        # Convertir a formato amigable para la plantilla
        activities = []
        for act in activities_raw:
            activities.append({
                "id": act[0],
                "action": act[1],
                "timestamp": act[2],
                "usuario": {
                    "usuario": act[3],
                    "nombre": act[4]
                } if act[3] else None
            })
        
        # Preparar los datos para el gráfico usando SQL nativo para el recuento
        activity_count_query = text("SELECT COUNT(*) FROM activity_log")
        activity_count = db.execute(activity_count_query).scalar()
        
        # Preparar datos del gráfico
        chart_data = prepare_activity_data(activities)
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "user": current_user,
            "user_count": user_count,
            "activities": activities[:10],  # Mostrar las últimas 10 en la lista
            "chart_data": chart_data,
            "activity_count": activity_count
        })
    
    @router.get("/perfil")
    async def user_perfil(request: Request, user: UserDB = Depends(get_current_user)):
        return templates.TemplateResponse("/usuarios/usuario_admin.html", {
            "request": request,
            "user": user
        })
    
    @router.post("/perfil")
    async def update_perfil(
        request: Request,
        nombre: str = Form(...),
        telefono: str = Form(...),
        email: str = Form(...),
        direccion: str = Form(...),
        fecha_nacimiento: str = Form(None),  # Cambiado de ... a None para hacerlo opcional
        password: str = Form(None),
        db: Session = Depends(get_db),
        user: UserDB = Depends(get_current_user)
    ):

        # Actualizar los datos del usuario en la base de datos
        user.nombre = nombre
        user.telefono = telefono
        user.mail = email  # Asegúrate de que el campo se llame "mail" y no "email"
        user.direccion = direccion
        user.fecha_nacimiento = fecha_nacimiento
        if password:
            user.clave = encriptar_clave(password)  # Asegúrate de que el campo se llame "clave"
            
        # Actualizar el usuario en la base de datos
        db_user = db.query(usuarios).filter(usuarios.codigo == user.codigo).first()
        if db_user:
            db_user.nombre = user.nombre
            db_user.telefono = user.telefono
            db_user.mail = user.mail
            db_user.direccion = user.direccion
            db_user.fecha_nacimiento = user.fecha_nacimiento
            if password:
                db_user.clave = user.clave
                
            db.commit()
            db.refresh(db_user)
        
        return templates.TemplateResponse("/usuarios/usuario_admin.html", {
            "request": request,
            "user": user,
            "message": "Perfil actualizado exitosamente"
        })

    @router.get("/")
    async def read_admin(user: dict = Depends(get_current_user)):
        return {"message": "Admin content"}

    @router.get("/nonexistent")
    async def read_nonexistent():
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    app.include_router(router)
    
    return router

from collections import defaultdict
from datetime import timezone
def prepare_activity_data(activities):
    """Prepara los datos de actividad para su visualización en gráficos"""
    activity_counts = defaultdict(lambda: defaultdict(int))
    
    for activity in activities:
        # Verificar si es un diccionario o un objeto
        if isinstance(activity, dict):
            # Es un diccionario
            usuario_info = activity.get("usuario")
            timestamp = activity.get("timestamp")
            
            if usuario_info:
                user_name = usuario_info.get("nombre", "Desconocido")
            else:
                user_name = "Desconocido"
        else:
            # Es un objeto
            usuario_info = getattr(activity, "usuario", None)
            timestamp = getattr(activity, "timestamp", None)
            
            if usuario_info:
                user_name = getattr(usuario_info, "nombre", "Desconocido")
            else:
                user_name = "Desconocido"
        
        # Verificar si timestamp es None
        if timestamp:
            # Convertir a formato de fecha
            if hasattr(timestamp, "tzinfo"):
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                local_timestamp = timestamp.astimezone()
                date_str = local_timestamp.date().isoformat()
            else:
                # Si no es un objeto datetime, convertir a string
                date_str = str(timestamp).split()[0]
            
            # Incrementar contador para este usuario y fecha
            activity_counts[user_name][date_str] += 1
    
    # Preparar los datos para Chart.js
    datasets = []
    colors = ['rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)', 
              'rgba(255, 206, 86, 0.5)', 'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)', 'rgba(255, 159, 64, 0.5)']
    
    for i, (user, dates) in enumerate(activity_counts.items()):
        color = colors[i % len(colors)]  # Ciclar colores si hay más usuarios que colores
        
        data = []
        for date_str, count in dates.items():
            data.append({'x': date_str, 'y': count})
            
        datasets.append({
            'label': user,
            'data': sorted(data, key=lambda x: x['x']),  # Ordenar por fecha
            'backgroundColor': color,
            'borderColor': color.replace('0.5', '1.0'),
            'borderWidth': 1
        })
    
    return {'datasets': datasets}