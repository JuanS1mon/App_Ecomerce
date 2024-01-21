from fastapi import APIRouter, status, Depends
from ..db.schemas.articulos import Articulos
from sqlalchemy.orm import Session
from ..db.crud import articulos as crud_articulos
from ..db.database import get_db
import time

router = APIRouter(prefix="/Articulos", 
                   tags=["Articulos"], 
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No Encontrado"}})

@router.get("/", response_model=list[Articulos]) 
def read_articulos(db: Session = Depends(get_db)): 
    start_time = time.time()
    articulos = crud_articulos.get_articulos(db)
    end_time = time.time()
    execution_time = end_time - start_time
    num_articulos = len(articulos)
    print(f"Execution time: {execution_time} seconds")
    print(f"Number of articles processed: {num_articulos}")
    return articulos