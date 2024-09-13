
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_producto import producto, productoRead
from db.crud.Maestro.Crud_producto import  create_producto , get_producto, gets_producto, delete_producto, get_producto_nombre,update_producto

router = APIRouter(
    prefix="/producto",
    tags=["producto"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/producto.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[productoRead])
async def routes_Post_producto (producto: producto, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if producto.codigo is None or producto.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_producto = get_producto_nombre(db, nombre=producto.nombre)
    if resultado_producto is None:
        db_producto = create_producto(db=db, codigo=producto.codigo, nombre=producto.nombre, fabricante=producto.fabricante, modelo=producto.modelo)
        return db_producto
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: nombre se encuentra registrado anteriormente en producto ")

@router.get("/{codigo}", response_model=list[productoRead]) 
async def routes_get_producto_codigo (codigo: int, db: Session = Depends(get_db)):  
    db_producto =  get_producto(db, codigo=codigo)
    if not db_producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: producto no encontrado")
    else:
        return db_producto
    
@router.get("/", response_model=list[productoRead]) 
async def routes_gets_producto_all (db: Session = Depends(get_db)):  
    db_producto = gets_producto(db)
    if not db_producto:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: productos no encontrados")
    else:
        return db_producto



@router.delete("/{codigo}", response_model=list[productoRead]) 
async def routes_delete_producto_numero(codigo: int, db: Session = Depends(get_db)):  
    resultado_producto =  get_producto(db, codigo=codigo)
    if not resultado_producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: producto no encontrado")
    else:
        db_producto = delete_producto(db, codigo=codigo)
        return db_producto

        
@router.put("/", response_model=list[productoRead]) 
async def routes_update_producto(producto: producto, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if producto.codigo is None or producto.nombre is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_producto(db, codigo=producto.codigo)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El codigo {producto.codigo} no existe en la tabla producto")
        else:
            resultado_producto = get_producto_nombre(db, descripcion=producto.nombre)
            if resultado_producto is None:
                db_producto = update_producto(db=db, codigo=producto.codigo, nombre=producto.nombre, fabricante=producto.fabricante, modelo=producto.modelo)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La nombre {producto.nombre} ya se encuentra en la tabla producto")
        return db_producto
