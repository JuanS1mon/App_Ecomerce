from fastapi import APIRouter,status, Depends
from db.database import  get_db
from db.schemas.modulos import Modulos
from sqlalchemy.orm import Session
from db.crud.modulos import gets


router = APIRouter(
    prefix="/modulos",
    tags=["modulos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)
# Rutas de la API
@router.get("/", response_model=list[Modulos])   #EndPoint
async def get_modulos(db: Session = Depends(get_db)):
    modulos = gets(db)
    return modulos