
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_Productos import Productos, ProductosRead
from db.crud.Maestro.Crud_Productos import  create_Productos , get_Productos, gets_Productos, delete_Productos, get_Productos_nombre,update_Productos

router = APIRouter(
    prefix="/Productos",
    tags=["Productos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/Productos.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[ProductosRead])
async def routes_Post_Productos (Productos: Productos, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if Productos.id is None or Productos.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_Productos = get_Productos_nombre(db, nombre=Productos.nombre)
    if resultado_Productos is None:
        db_Productos = create_Productos(db=db, id=Productos.id, nombre=Productos.nombre, descripcion=Productos.descripcion, precio=Productos.precio, stock_cantidad=Productos.stock_cantidad, Id_compania=Productos.Id_compania, created_at=Productos.created_at, updated_at=Productos.updated_at)
        return db_Productos
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: nombre se encuentra registrado anteriormente en Productos ")

@router.get("/{id}", response_model=list[ProductosRead]) 
async def routes_get_Productos_id (id: int, db: Session = Depends(get_db)):  
    db_Productos =  get_Productos(db, id=id)
    if not db_Productos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: Productos no encontrado")
    else:
        return db_Productos
    
@router.get("/", response_model=list[ProductosRead]) 
async def routes_gets_Productos_all (db: Session = Depends(get_db)):  
    db_Productos = gets_Productos(db)
    if not db_Productos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: Productoss no encontrados")
    else:
        return db_Productos



@router.delete("/{id}", response_model=list[ProductosRead]) 
async def routes_delete_Productos_numero(id: int, db: Session = Depends(get_db)):  
    resultado_Productos =  get_Productos(db, id=id)
    if not resultado_Productos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: Productos no encontrado")
    else:
        db_Productos = delete_Productos(db, id=id)
        return db_Productos

        
@router.put("/", response_model=list[ProductosRead]) 
async def routes_update_Productos(Productos: Productos, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if Productos.id is None or Productos.nombre is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_Productos(db, codigo=Productos.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {Productos.id} no existe en la tabla Productos")
        else:
            resultado_Productos = get_Productos_nombre(db, descripcion=Productos.nombre)
            if resultado_Productos is None:
                db_Productos = update_Productos(db=db, id=Productos.id, nombre=Productos.nombre, descripcion=Productos.descripcion, precio=Productos.precio, stock_cantidad=Productos.stock_cantidad, Id_compania=Productos.Id_compania, created_at=Productos.created_at, updated_at=Productos.updated_at)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La nombre {Productos.nombre} ya se encuentra en la tabla Productos")
        return db_Productos
