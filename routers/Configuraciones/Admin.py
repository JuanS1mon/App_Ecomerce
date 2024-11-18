import os
import re
from fastapi import FastAPI, Request, APIRouter, status, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from Services.security.security import get_current_user  # Importar la función de seguridad
from db.database import get_db
from db.models.usuarios import usuarios 
from db.models.activityLog import ActivityLog
from datetime import date, timedelta


templates = Jinja2Templates(directory="static")

def create_admin_router(app: FastAPI):
    router = APIRouter(
        prefix="/admin",
        tags=["Admin"],
        responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
    )

    @router.get("/page")
    async def admin(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
        routes = extract_route_names()
        # Contar la cantidad de usuarios en la base de datos
        user_count = db.query(usuarios).count()
        
        # Filtrar actividades de los últimos 7 días
        seven_days_ago = date.today() - timedelta(days=7)
        activities = db.query(ActivityLog).filter(ActivityLog.timestamp >= seven_days_ago).order_by(ActivityLog.timestamp.desc()).all()
        
        # Preparar los datos para el gráfico
        chart_data = prepare_activity_data(activities)

        #contar la cantidad de actividades
        activity_count = db.query(ActivityLog).count()

        return templates.TemplateResponse("html/admin.html", {
            "request": request,
            "routes": routes,
            "user": current_user,
            "user_count": user_count,
            "activities": activities[:10],  # Mostrar las últimas 10 en la lista si es necesario
            "chart_data": chart_data,
            "activity_count": activity_count
        })

    @router.get("/")
    async def read_admin(user: dict = Depends(get_current_user)):
        return {"message": "Admin content"}

    @router.get("/nonexistent")
    async def read_nonexistent():
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    app.include_router(router)
    
    return router

def extract_route_names():
    # Obtener la ruta absoluta del directorio que contiene este script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Construir la ruta al archivo main.py
    main_path = os.path.join(dir_path, '../../main.py')

    try:
        with open(main_path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        return []

    # Buscar el inicio y el fin de la sección de rutas
    start = data.find('#Inicio Router de la API')
    end = data.find('#Fin Router de la API')

    # Si no se encontraron las marcas de inicio o fin, devolver una lista vacía
    if start == -1 or end == -1:
        return []

    # Extraer la sección de rutas
    routes_section = data[start:end]

    # Buscar todas las líneas que incluyen 'app.include_router'
    route_lines = re.findall(r'app\.include_router\((.*?)\)', routes_section)

    # Extraer los nombres de las rutas
    route_names = [line.split('.')[0].replace('Route_', '') for line in route_lines]

    return route_names

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