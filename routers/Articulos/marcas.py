from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import Session
from db.database import  get_db
from db.schemas.Articulos.marcas import Marca,MarcaCreate
from db.crud.Articulos.marcas import get,gets,create,delete,update,get_descripcion


router = APIRouter(
    prefix="/marcas",
    tags=["Marcas"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

#response_model es el modelo que se va a utilizar para validar la entrada de datos y convertir los datos en diferentes formatos.
#crea_marca es el nombre de la funcion que se va a llamar desde el main 
#marca es el nombre de la variable que se va a recibir desde el main
#MarcaCreate es el modelo que se va a utilizar para validar la entrada de datos y convertir los datos en diferentes formatos.    

@router.post("/", response_model=list[Marca]) #Marca schema que devuelve 2 datos codigo y descripcion
async def post_Marca(Marca: MarcaCreate, db: Session = Depends(get_db)):#marcacreate recibe 1 dato descripcion
    db_Marca = get_descripcion(db, descripcion=Marca.descripcion)
    if db_Marca is None:
        result = create(db=db, descripcion=Marca.descripcion)
        return result
    else:
        raise HTTPException(status_code=402, detail="La Marca se encuentra registrada")



@router.get("/{codigo}", response_model=list[Marca]) # Lista para un solo resultado
async def get_marca(codigo: int, db: Session = Depends(get_db)):
    marca = get(db, codigo=codigo)
    return marca


@router.get("/", response_model=list[Marca]) # Lista para mas de un resultado
async def get_marcas(db: Session = Depends(get_db)):
    marcas = gets(db)
    return marcas



@router.delete("/{codigo}", response_model=list[Marca])
async def delete_marca(codigo: int, db: Session = Depends(get_db)):
    # Intenta obtener la marca con el código proporcionado
    db_marca = get(db, codigo=codigo) 
    # Si la marca no existe o es una lista vacía, lanza una excepción
    if db_marca is None or db_marca == []:
        raise HTTPException(status_code=404, detail="La marca no existe o ya fue eliminada")
    # Si la marca existe, la elimina de la base de datos
    delete(db=db, codigo=codigo)
    # Devuelve la marca que se eliminó
    return db_marca


@router.put("/{codigo}", response_model=list[Marca])
async def update_marca(codigo: int, marca: MarcaCreate, db: Session = Depends(get_db)):
    # Intenta obtener la marca con el código proporcionado
    db_marca = get(db, codigo=codigo)
    # Si la marca no existe, lanza una excepción
    if db_marca is None or db_marca == []:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    # Si la marca existe, la actualiza en la base de datos
    updated_marca = update(db=db, codigo=codigo, descripcion=marca.descripcion)
    # Devuelve la marca que se actualizó
    return updated_marca