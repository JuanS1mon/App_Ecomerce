
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_inventarios import inventarios, inventariosRead
from db.crud.Maestro.Crud_inventarios import  create_inventarios , get_inventarios, gets_inventarios, delete_inventarios, get_inventarios_producto_id,update_inventarios

router = APIRouter(
    prefix="/inventarios",
    tags=["inventarios"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/inventarios.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[inventariosRead])
async def routes_Post_inventarios (inventarios: inventarios, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if inventarios.id is None or inventarios.producto_id is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_inventarios = get_inventarios_producto_id(db, producto_id=inventarios.producto_id)
    if resultado_inventarios is None:
        db_inventarios = create_inventarios(db=db, id=inventarios.id, producto_id=inventarios.producto_id, cantidad_fisica=inventarios.cantidad_fisica, inventario_date=inventarios.inventario_date, notas=inventarios.notas, created_at=inventarios.created_at, updated_at=inventarios.updated_at)
        return db_inventarios
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: producto_id se encuentra registrado anteriormente en inventarios ")

@router.get("/{id}", response_model=list[inventariosRead]) 
async def routes_get_inventarios_id (id: int, db: Session = Depends(get_db)):  
    db_inventarios =  get_inventarios(db, id=id)
    if not db_inventarios:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: inventarios no encontrado")
    else:
        return db_inventarios
    
@router.get("/", response_model=list[inventariosRead]) 
async def routes_gets_inventarios_all (db: Session = Depends(get_db)):  
    db_inventarios = gets_inventarios(db)
    if not db_inventarios:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: inventarioss no encontrados")
    else:
        return db_inventarios



@router.delete("/{id}", response_model=list[inventariosRead]) 
async def routes_delete_inventarios_numero(id: int, db: Session = Depends(get_db)):  
    resultado_inventarios =  get_inventarios(db, id=id)
    if not resultado_inventarios:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: inventarios no encontrado")
    else:
        db_inventarios = delete_inventarios(db, id=id)
        return db_inventarios

        
@router.put("/", response_model=list[inventariosRead]) 
async def routes_update_inventarios(inventarios: inventarios, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if inventarios.id is None or inventarios.producto_id is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_inventarios(db, codigo=inventarios.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {inventarios.id} no existe en la tabla inventarios")
        else:
            resultado_inventarios = get_inventarios_producto_id(db, descripcion=inventarios.producto_id)
            if resultado_inventarios is None:
                db_inventarios = update_inventarios(db=db, id=inventarios.id, producto_id=inventarios.producto_id, cantidad_fisica=inventarios.cantidad_fisica, inventario_date=inventarios.inventario_date, notas=inventarios.notas, created_at=inventarios.created_at, updated_at=inventarios.updated_at)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La producto_id {inventarios.producto_id} ya se encuentra en la tabla inventarios")
        return db_inventarios
