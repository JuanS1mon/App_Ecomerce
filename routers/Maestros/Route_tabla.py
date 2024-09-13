
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_tabla import tabla, tablaRead
from db.crud.Maestro.Crud_tabla import  create_tabla , get_tabla, gets_tabla, delete_tabla, get_tabla_campo2,update_tabla

router = APIRouter(
    prefix="/tabla",
    tags=["tabla"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/tabla.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[tablaRead])
async def routes_Post_tabla (tabla: tabla, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if tabla.campo1 is None or tabla.campo2 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_tabla = get_tabla_campo2(db, campo2=tabla.campo2)
    if resultado_tabla is None:
        db_tabla = create_tabla(db=db, campo1=tabla.campo1, campo2=tabla.campo2, campo3=tabla.campo3, campo4=tabla.campo4)
        return db_tabla
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: campo2 se encuentra registrado anteriormente en tabla ")

@router.get("/{campo1}", response_model=list[tablaRead]) 
async def routes_get_tabla_campo1 (campo1: int, db: Session = Depends(get_db)):  
    db_tabla =  get_tabla(db, campo1=campo1)
    if not db_tabla:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: tabla no encontrado")
    else:
        return db_tabla
    
@router.get("/", response_model=list[tablaRead]) 
async def routes_gets_tabla_all (db: Session = Depends(get_db)):  
    db_tabla = gets_tabla(db)
    if not db_tabla:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: tablas no encontrados")
    else:
        return db_tabla



@router.delete("/{campo1}", response_model=list[tablaRead]) 
async def routes_delete_tabla_numero(campo1: int, db: Session = Depends(get_db)):  
    resultado_tabla =  get_tabla(db, campo1=campo1)
    if not resultado_tabla:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: tabla no encontrado")
    else:
        db_tabla = delete_tabla(db, campo1=campo1)
        return db_tabla

        
@router.put("/", response_model=list[tablaRead]) 
async def routes_update_tabla(tabla: tabla, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if tabla.campo1 is None or tabla.campo2 is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_tabla(db, codigo=tabla.campo1)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El campo1 {tabla.campo1} no existe en la tabla tabla")
        else:
            resultado_tabla = get_tabla_campo2(db, descripcion=tabla.campo2)
            if resultado_tabla is None:
                db_tabla = update_tabla(db=db, campo1=tabla.campo1, campo2=tabla.campo2, campo3=tabla.campo3, campo4=tabla.campo4)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La campo2 {tabla.campo2} ya se encuentra en la tabla tabla")
        return db_tabla
