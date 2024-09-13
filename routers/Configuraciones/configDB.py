from fastapi import FastAPI, Request, APIRouter, status,Depends
from fastapi.templating import Jinja2Templates
from Services.security.security import get_current_user

import json
from dotenv import dotenv_values


templates = Jinja2Templates(directory="static")

router = APIRouter(
    prefix="/configdb",
    tags=["configdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/")
async def configdb(request: Request, current_user: dict = Depends(get_current_user)):
    env_values=get_env_values()

    # Pasar los valores a la plantilla
    return templates.TemplateResponse("html/configdb.html", {"request": request, "env_values": env_values})


def get_env_values():
    env_values = dotenv_values()
    return env_values

def update_env_values(data):
    with open('.env', 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        key, value = line.strip().split('=')
        if key in data:
            value = data[key]
        updated_lines.append(f'{key}={value}\n')

    with open('.env', 'w') as file:
        file.writelines(updated_lines)