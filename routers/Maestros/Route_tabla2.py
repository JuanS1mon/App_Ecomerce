
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_tabla2 import tabla2, tabla2Read
from db.crud.Maestro.Crud_tabla2 import  create_tabla2 , get_tabla2, gets_tabla2, delete_tabla2, get_tabla2_descripcion,update_tabla2

router = APIRouter(
    prefix="/tabla2",
    tags=["tabla2"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/tabla2.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[tabla2Read])
async def routes_Post_tabla2 (tabla2: tabla2, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if tabla2.codigo is None or tabla2.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_tabla2 = get_tabla2_descripcion(db, descripcion=tabla2.descripcion)
    if resultado_tabla2 is None:
        db_tabla2 = create_tabla2(db=db, codigo=tabla2.codigo, descripcion=tabla2.descripcion)
        return db_tabla2
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: descripcion se encuentra registrado anteriormente en tabla2 ")

@router.get("/{codigo}", response_model=list[tabla2Read]) 
async def routes_get_tabla2_codigo (codigo: int, db: Session = Depends(get_db)):  
    db_tabla2 =  get_tabla2(db, codigo=codigo)
    if not db_tabla2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: tabla2 no encontrado")
    else:
        return db_tabla2
    
@router.get("/", response_model=list[tabla2Read]) 
async def routes_gets_tabla2_all (db: Session = Depends(get_db)):  
    db_tabla2 = gets_tabla2(db)
    if not db_tabla2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: tabla2s no encontrados")
    else:
        return db_tabla2



@router.delete("/{codigo}", response_model=list[tabla2Read]) 
async def routes_delete_tabla2_numero(codigo: int, db: Session = Depends(get_db)):  
    resultado_tabla2 =  get_tabla2(db, codigo=codigo)
    if not resultado_tabla2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: tabla2 no encontrado")
    else:
        db_tabla2 = delete_tabla2(db, codigo=codigo)
        return db_tabla2

        
@router.put("/", response_model=list[tabla2Read]) 
async def routes_update_tabla2(tabla2: tabla2, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if tabla2.codigo is None or tabla2.descripcion is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_tabla2(db, codigo=tabla2.codigo)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El codigo {tabla2.codigo} no existe en la tabla tabla2")
        else:
            resultado_tabla2 = get_tabla2_descripcion(db, descripcion=tabla2.descripcion)
            if resultado_tabla2 is None:
                db_tabla2 = update_tabla2(db=db, codigo=tabla2.codigo, descripcion=tabla2.descripcion)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La descripcion {tabla2.descripcion} ya se encuentra en la tabla tabla2")
        return db_tabla2
