
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_pruebe import pruebe, pruebeRead
from db.crud.Maestro.Crud_pruebe import create_pruebe, get_pruebe, get_pruebe_by_campoq, gets_pruebe, delete_pruebe, update_pruebe

router = APIRouter(
    prefix="/pruebe",
    tags=["pruebe"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/pruebe.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=pruebeRead)
async def routes_post_pruebe(pruebe: pruebe, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if pruebe.campoq is None or pruebe.campob is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    resultado_pruebe = get_pruebe_by_campoq(db, campob=pruebe.campoq)
    if resultado_pruebe is None:
        db_pruebe = create_pruebe(db=db, campoq=pruebe.campoq, campob=pruebe.campob, campoc=pruebe.campoc)
        return db_pruebe
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: campob se encuentra registrado anteriormente en pruebe")

@router.get("/{campoq}", response_model=pruebeRead)
async def routes_get_pruebe_campoq(campoq: int, db: Session = Depends(get_db)):
    db_pruebe = get_pruebe(db, campoq=campoq)
    if not db_pruebe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: pruebe no encontrado")
    return db_pruebe

@router.get("/", response_model=list[pruebeRead])
async def routes_gets_pruebe_all(db: Session = Depends(get_db)):
    db_pruebe = gets_pruebe(db)
    if not db_pruebe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: pruebes no encontrados")
    return db_pruebe

@router.delete("/{campoq}", response_model=pruebeRead)
async def routes_delete_pruebe_numero(campoq: int, db: Session = Depends(get_db)):
    resultado_pruebe = get_pruebe(db, campoq=campoq)
    if not resultado_pruebe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: pruebe no encontrado")
    db_pruebe = delete_pruebe(db, campoq=campoq)
    return db_pruebe

@router.put("/", response_model=pruebeRead)
async def routes_update_pruebe(pruebe: pruebe, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if pruebe.campoq is None or pruebe.campob is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    resultado_codigo = get_pruebe(db, codigo=pruebe.campoq)
    if resultado_codigo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El campoq {pruebe.campoq} no existe en la tabla pruebe")
    resultado_pruebe = get_pruebe_by_campoq(db, campob=pruebe.campob)
    if resultado_pruebe is None:
        db_pruebe = update_pruebe(db=db, campoq=pruebe.campoq, campob=pruebe.campob, campoc=pruebe.campoc)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La campob {pruebe.campoq} ya se encuentra en la tabla pruebe")
    return db_pruebe

@router.get("/count", response_model=int)
async def routes_count_pruebe(db: Session = Depends(get_db)):
    count = db.query(pruebe).count()
    return count

@router.get("/search", response_model=list[pruebeRead])
async def routes_search_pruebe(q: str, db: Session = Depends(get_db)):
    results = db.query(pruebe).filter(pruebe.campob.contains(q)).all()
    return results

@router.get("/paginate", response_model=list[pruebeRead])
async def routes_paginate_pruebe(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    results = db.query(pruebe).offset(skip).limit(limit).all()
    return results
