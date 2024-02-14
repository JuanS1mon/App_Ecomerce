from fastapi import APIRouter, HTTPException, status, Depends
from db.schemas.asientos import Asiento,AsientoRespuesta,Asiento_respuesta,AsientoRespuestas
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.crud.asientos import get,gets,create,delete,update
from db.database import  get_db
from starlette.responses import FileResponse
from typing import List

router = APIRouter(
    prefix="/contabilidad",
    tags=["Ccntabilidad"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)



# LA EMPRESA TIENE QUE SER LA DE SISTEMA O LA QUE SE ESTE USANDO EN EL MOMENTO ???????????  Fue la tomo de sistema

@router.get("/")
async def read_root():
    return FileResponse('static/contabilidad.html')

@router.get("/consultar")
async def read_root():
    return FileResponse('static/asientosconsulta.html')

@router.get("/nuevoasiento")
async def read_root():
    return FileResponse('static/nuevo_asientos.html')
# Rutas para el CRUD de Asientos 

# Ruta para crear un nuevo Asiento

@router.post("/nuevoasiento", response_model=Asiento_respuesta) #Asiento schema que devuelve 2 datos codigo y descripcion
async def post_Asiento(Asiento: Asiento, db: Session = Depends(get_db)):#AsientoCreate recibe datos de asiento
    # Calcula la suma de los importes con signo "D" y "H"
    suma_D = sum(detalle.importe for detalle in Asiento.asiento_detalle if detalle.signo == "D")
    suma_H = sum(detalle.importe for detalle in Asiento.asiento_detalle if detalle.signo == "H")

    # Comprueba si las sumas son iguales
    if suma_D != suma_H:
        raise HTTPException(status_code=410, detail="La suma de los importes con signo 'D' no es igual a la suma de los importes con signo 'H'")

    try:
        result = create(db=db, fecha=Asiento.fecha, detalle=Asiento.detalle, tipomovimiento=Asiento.tipomovimiento, asiento_detalle=Asiento.asiento_detalle)
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail='Ups :( No se pudo crear el asiento, reintente nuevamente')



# Ruta para obtener un Asiento por su código
@router.get("/{codigo}", response_model=AsientoRespuesta)
async def get_Asiento(codigo: str, db: Session = Depends(get_db)):
    print(codigo)
    try:
        codigo_asiento = int(codigo)
    except ValueError:
        raise HTTPException(status_code=400, detail="El código del asiento debe ser un número entero válido")

    asiento = get(db, asiento=codigo_asiento)
    if asiento is None:
        raise HTTPException(status_code=404, detail="Asiento no encontrado") 
    return asiento


@router.post("/asientos", response_model=List[AsientoRespuestas])
async def post_Asientos(busqueda: dict, db: Session = Depends(get_db)):
    try:
        if busqueda.get('codigos_asientos'):
            busqueda['codigos_asientos'] = [int(codigo) for codigo in busqueda['codigos_asientos']]
        if busqueda.get('TipodeMovimiento'):
            if any(tipo < 0 for tipo in busqueda['TipodeMovimiento']):
                raise HTTPException(status_code=400, detail="Los tipos de movimiento deben ser números enteros positivos")
    except ValueError:
        raise HTTPException(status_code=400, detail="Los códigos de los asientos y los tipos de movimiento deben ser números enteros válidos")
    asientos = gets(db, busqueda.get('fechadesde'), busqueda.get('fechahasta'), busqueda.get('TipodeMovimiento'), busqueda.get('codigos_asientos'))
    if not asientos:
        raise HTTPException(status_code=404, detail="Asientos no encontrados") 
    return asientos

    

@router.delete("/{asiento}")
async def delete_Asiento(asiento: int, db: Session = Depends(get_db)):
    print("delete")
    # Intenta obtener la Asiento con el código proporcionado
    db_Asiento = get(db, asiento=asiento) 
    print(db_Asiento)
    # Si la Asiento no existe o es una lista vacía, lanza una excepción
    if db_Asiento is None or db_Asiento == []:
        raise HTTPException(status_code=404, detail="La Asiento no existe o ya fue eliminada")
    # Si la Asiento existe, la elimina de la base de datos
    delete(db=db, asiento=asiento)
    # Devuelve la Asiento que se eliminó
    return db_Asiento


@router.put("/{codigo}", response_model=Asiento_respuesta)
async def update_Asiento(codigo: int, asiento: Asiento, db: Session = Depends(get_db)):
    # Intenta obtener la Asiento con el código proporcionado
    db_Asiento = get(db, codigo=codigo)
    # Si la Asiento no existe, lanza una excepción
    if db_Asiento is None:
        raise HTTPException(status_code=404, detail="Asiento no encontrada")
    # Si la Asiento existe, la actualiza en la base de datos
    updated_Asiento = update(db=db, codigo=codigo, asiento=asiento)
    # Devuelve la Asiento que se actualizó
    return updated_Asiento