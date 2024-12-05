
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_products import ProductsCreate, ProductsUpdate, ProductsRead
from db.models.products import Products as ProductsModel
from db.crud.Maestro.Crud_products import create_products, get_products, gets_products, delete_products, update_products
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ProductsRead)
async def routes_post_products(products: ProductsCreate, db: Session = Depends(get_db)):

    # Validación de campos requeridos
    if products.id is None or products.name is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    products_model = ProductsModel(**products.model_dump())
    db_products = create_products(db=db, products=products_model)
    return ProductsRead.model_validate(db_products)


@router.get("/id/{id}", response_model=ProductsRead)
async def routes_get_products_id(id: int, db: Session = Depends(get_db)):
    db_products = get_products(db, id)
    if not db_products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: products no encontrado")
    return ProductsRead.model_validate(db_products)

@router.get("/", response_model=list[ProductsRead])
async def routes_gets_products_all(db: Session = Depends(get_db)):
    db_products = gets_products(db)
    if not db_products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: productss no encontrados")
    return [ProductsRead.model_validate(products) for products in db_products]

@router.delete("/id/{id}", response_model=ProductsRead)
async def routes_delete_products_numero(id: int, db: Session = Depends(get_db)):
    resultado_products = get_products(db, id)
    if not resultado_products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: products no encontrado")
    db_products = delete_products(db, id)
    return ProductsRead.model_validate(db_products)


@router.put("/id/{id}", response_model=ProductsRead)
async def routes_update_products(id: int, products: ProductsUpdate, db: Session = Depends(get_db)):
    # Convertir el objeto Pydantic a diccionario
    products_data = products.model_dump()

    # Actualizar el registro existente
    db_products = update_products(db=db, id=id, products_data=products_data)
    return ProductsRead.model_validate(db_products)

@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    with open("static/html/products.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
