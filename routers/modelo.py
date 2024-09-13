from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import Session
from db.database import  get_db
from db.schemas.Modelo import modelo,modeloCreate
from db.crud.modelo import get,gets,create,delete,update,get_descripcion


router = APIRouter(
    prefix="/modelo",
    tags=["modelo"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

#response_model es el modelo que se va a utilizar para validar la entrada de datos y convertir los datos en diferentes formatos.
#crea_modelo es el nombre de la funcion que se va a llamar desde el main 
#modelo es el nombre de la variable que se va a recibir desde el main
#modeloCreate es el modelo que se va a utilizar para validar la entrada de datos y convertir los datos en diferentes formatos.    

@router.post("/", response_model=list[modelo]) #modelo schema que devuelve 2 datos codigo y descripcion
async def post_modelo(modelo: modeloCreate, db: Session = Depends(get_db)):#modelocreate recibe 1 dato descripcion
    db_modelo = get_descripcion(db, descripcion=modelo.descripcion)
    if db_modelo is None:
        result = create(db=db, descripcion=modelo.descripcion)
        return result
    else:
        raise HTTPException(status_code=402, detail="La modelo se encuentra registrada")



@router.get("/{codigo}", response_model=list[modelo]) # Lista para un solo resultado
async def get_modelo(codigo: int, db: Session = Depends(get_db)):
    modelo = get(db, codigo=codigo)
    return modelo


@router.get("/", response_model=list[modelo]) # Lista para mas de un resultado
async def get_modelo(db: Session = Depends(get_db)):
    modelo = gets(db)
    return modelo



@router.delete("/{codigo}", response_model=list[modelo])
async def delete_modelo(codigo: int, db: Session = Depends(get_db)):
    # Intenta obtener la modelo con el código proporcionado
    db_modelo = get(db, codigo=codigo) 
    # Si la modelo no existe o es una lista vacía, lanza una excepción
    if db_modelo is None or db_modelo == []:
        raise HTTPException(status_code=404, detail="La modelo no existe o ya fue eliminada")
    # Si la modelo existe, la elimina de la base de datos
    delete(db=db, codigo=codigo)
    # Devuelve la modelo que se eliminó
    return db_modelo


@router.put("/{codigo}", response_model=list[modelo])
async def update_modelo(codigo: int, modelo: modeloCreate, db: Session = Depends(get_db)):
    # Intenta obtener la modelo con el código proporcionado
    db_modelo = get(db, codigo=codigo)
    # Si la modelo no existe, lanza una excepción
    if db_modelo is None or db_modelo == []:
        raise HTTPException(status_code=404, detail="modelo no encontrada")
    # Si la modelo existe, la actualiza en la base de datos
    updated_modelo = update(db=db, codigo=codigo, descripcion=modelo.descripcion)
    # Devuelve la modelo que se actualizó
    return updated_modelo