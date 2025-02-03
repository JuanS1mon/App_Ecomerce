import os
import re
from fastapi import FastAPI, Form, Request, APIRouter, status, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from Services.security.security import encriptar_clave, get_current_user  # Importar la función de seguridad
from db.database import get_db
from db.models.usuarios import usuarios 
from db.models.activityLog import ActivityLog
from datetime import date, timedelta
from db.schemas.Maestro.Usuarios import UserDB  # Asegúrate de importar UserDB

templates = Jinja2Templates(directory="static/html")  # Ajusta el directorio según sea necesario

def create_admin_router(app: FastAPI):
    router = APIRouter(
        prefix="/admin",
        tags=["Admin"],
        responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
    )

    @router.get("/page")
    async def admin_page(request: Request, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
        user_count = db.query(usuarios).count()
        # Filtrar actividades de los últimos 7 días
        #seven_days_ago = date.today() - timedelta(days=7)
        activities = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).all()

        # Preparar los datos para el gráfico
        chart_data = prepare_activity_data(activities)
    
        # Contar la cantidad de actividades
        activity_count = db.query(ActivityLog).count()
    
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "user": current_user,
            "user_count": user_count,
            "activities": activities[:10],  # Mostrar las últimas 10 en la lista si es necesario
            "chart_data": chart_data,
            "activity_count": activity_count
        })

    
    @router.get("/perfil")
    async def user_perfil(request: Request, user: UserDB = Depends(get_current_user)):
        return templates.TemplateResponse("admin_user.html", {
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
        fecha_nacimiento: str = Form(...),
        password: str = Form(None),
        db: Session = Depends(get_db),
        user: UserDB = Depends(get_current_user)
    ):
        # Actualizar los datos del usuario en la base de datos
        user.nombre = nombre
        user.telefono = telefono
        user.email = email
        user.direccion = direccion
        user.fecha_nacimiento = fecha_nacimiento
        if password:
            user.hashed_password = encriptar_clave(password)
        db.commit()
        db.refresh(user)
        
        return templates.TemplateResponse("admin_user.html", {
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
    activity_counts = defaultdict(lambda: defaultdict(int))

    for activity in activities:
        if activity.usuario:
            timestamp = activity.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            local_timestamp = timestamp.astimezone()
            date_str = local_timestamp.date().isoformat()
            user = activity.usuario.nombre
            activity_counts[user][date_str] += 1

    datasets = []
    color_palette = {
        user: color for user, color in zip(activity_counts.keys(), ['red', 'blue', 'green', 'orange', 'purple'])
    }

    for user, dates in activity_counts.items():
        data = []
        for date, count in dates.items():
            data.append({'x': date, 'y': count})
        user_data = {
            'label': user,
            'data': data,
            'backgroundColor': color_palette[user]
        }
        datasets.append(user_data)

    chart_data = {
        'datasets': datasets
    }
    return chart_data