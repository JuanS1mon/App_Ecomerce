def generate_route(module_name, field_names, field_types):
    """
    Genera el código de las rutas (endpoints) para un módulo dado.
    """
    # Convertir a minúsculas
    module_name = module_name.lower()
    field_names = [field_name.lower() for field_name in field_names]
    field_types = [field_type.lower() for field_type in field_types]

    # Genera las validaciones de campos requeridos
    field_validations = ' or '.join([f'{module_name}.{field_name} is None' for field_name in field_names[:2]])

    route_code = f"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_{module_name} import {module_name.capitalize()}Create, {module_name.capitalize()}Update, {module_name.capitalize()}Read
from db.models.{module_name} import {module_name.capitalize()} as {module_name.capitalize()}Model
from db.crud.Maestro.Crud_{module_name} import create_{module_name}, get_{module_name}, gets_{module_name}, delete_{module_name}, update_{module_name}
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(
    prefix="/{module_name}",
    tags=["{module_name}"],
    responses={{status.HTTP_404_NOT_FOUND: {{"message": "ruta no encontrada"}}}}
)

@router.post("/", response_model={module_name.capitalize()}Read)
async def routes_post_{module_name}({module_name}: {module_name.capitalize()}Create, db: Session = Depends(get_db)):

    # Validación de campos requeridos
    if {field_validations}:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    {module_name}_model = {module_name.capitalize()}Model(**{module_name}.model_dump())
    db_{module_name} = create_{module_name}(db=db, {module_name}={module_name}_model)
    return {module_name.capitalize()}Read.model_validate(db_{module_name})


@router.get("/id/{{{field_names[0]}}}", response_model={module_name.capitalize()}Read)
async def routes_get_{module_name}_{field_names[0]}({field_names[0]}: {field_types[0]}, db: Session = Depends(get_db)):
    db_{module_name} = get_{module_name}(db, {field_names[0]})
    if not db_{module_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: {module_name} no encontrado")
    return {module_name.capitalize()}Read.model_validate(db_{module_name})

@router.get("/", response_model=list[{module_name.capitalize()}Read])
async def routes_gets_{module_name}_all(db: Session = Depends(get_db)):
    db_{module_name} = gets_{module_name}(db)
    if not db_{module_name}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: {module_name}s no encontrados")
    return [{module_name.capitalize()}Read.model_validate({module_name}) for {module_name} in db_{module_name}]

@router.delete("/id/{{{field_names[0]}}}", response_model={module_name.capitalize()}Read)
async def routes_delete_{module_name}_numero({field_names[0]}: {field_types[0]}, db: Session = Depends(get_db)):
    resultado_{module_name} = get_{module_name}(db, {field_names[0]})
    if not resultado_{module_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: {module_name} no encontrado")
    db_{module_name} = delete_{module_name}(db, {field_names[0]})
    return {module_name.capitalize()}Read.model_validate(db_{module_name})


@router.put("/id/{{{field_names[0]}}}", response_model={module_name.capitalize()}Read)
async def routes_update_{module_name}({field_names[0]}: {field_types[0]}, {module_name}: {module_name.capitalize()}Update, db: Session = Depends(get_db)):
    # Convertir el objeto Pydantic a diccionario
    {module_name}_data = {module_name}.model_dump()

    # Actualizar el registro existente
    db_{module_name} = update_{module_name}(db=db, {field_names[0]}={field_names[0]}, {module_name}_data={module_name}_data)
    return {module_name.capitalize()}Read.model_validate(db_{module_name})

@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    with open("static/html/{module_name}.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
"""
    return route_code