
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_transactiones import transactiones, transactionesRead
from db.crud.Maestro.Crud_transactiones import  create_transactiones , get_transactiones, gets_transactiones, delete_transactiones, get_transactiones_producto_id,update_transactiones

router = APIRouter(
    prefix="/transactiones",
    tags=["transactiones"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/transactiones.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[transactionesRead])
async def routes_Post_transactiones (transactiones: transactiones, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if transactiones.id is None or transactiones.producto_id is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_transactiones = get_transactiones_producto_id(db, producto_id=transactiones.producto_id)
    if resultado_transactiones is None:
        db_transactiones = create_transactiones(db=db, id=transactiones.id, producto_id=transactiones.producto_id, cantidad=transactiones.cantidad, transaction_tipo=transactiones.transaction_tipo, transaction_date=transactiones.transaction_date, usuario_id=transactiones.usuario_id, created_at=transactiones.created_at, updated_at=transactiones.updated_at)
        return db_transactiones
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: producto_id se encuentra registrado anteriormente en transactiones ")

@router.get("/{id}", response_model=list[transactionesRead]) 
async def routes_get_transactiones_id (id: int, db: Session = Depends(get_db)):  
    db_transactiones =  get_transactiones(db, id=id)
    if not db_transactiones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: transactiones no encontrado")
    else:
        return db_transactiones
    
@router.get("/", response_model=list[transactionesRead]) 
async def routes_gets_transactiones_all (db: Session = Depends(get_db)):  
    db_transactiones = gets_transactiones(db)
    if not db_transactiones:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: transactioness no encontrados")
    else:
        return db_transactiones



@router.delete("/{id}", response_model=list[transactionesRead]) 
async def routes_delete_transactiones_numero(id: int, db: Session = Depends(get_db)):  
    resultado_transactiones =  get_transactiones(db, id=id)
    if not resultado_transactiones:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: transactiones no encontrado")
    else:
        db_transactiones = delete_transactiones(db, id=id)
        return db_transactiones

        
@router.put("/", response_model=list[transactionesRead]) 
async def routes_update_transactiones(transactiones: transactiones, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if transactiones.id is None or transactiones.producto_id is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_transactiones(db, codigo=transactiones.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {transactiones.id} no existe en la tabla transactiones")
        else:
            resultado_transactiones = get_transactiones_producto_id(db, descripcion=transactiones.producto_id)
            if resultado_transactiones is None:
                db_transactiones = update_transactiones(db=db, id=transactiones.id, producto_id=transactiones.producto_id, cantidad=transactiones.cantidad, transaction_tipo=transactiones.transaction_tipo, transaction_date=transactiones.transaction_date, usuario_id=transactiones.usuario_id, created_at=transactiones.created_at, updated_at=transactiones.updated_at)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La producto_id {transactiones.producto_id} ya se encuentra en la tabla transactiones")
        return db_transactiones
