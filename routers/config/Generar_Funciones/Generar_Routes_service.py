def generate_route(module_name, field_names, field_types):
    """
    Genera el código de las rutas (endpoints) para un módulo dado.
    """
    # Convertir a minúsculas
    module_name = module_name.lower()
    module_class_name = module_name.capitalize()
    primary_key = field_names[0]
    primary_key_type = field_types[0].lower()

    # Genera las validaciones de campos requeridos
    field_validations = ' or '.join([f'{module_name}.{field_name} is None' for field_name in field_names[:2]])

    # Rutas de importaciones relativas para la estructura de servicios
    route_code = f"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
try:
    from ...db.database import get_db
except ImportError:
    from sql_app.db.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/{module_name}",
    tags=["{module_name}"],
    responses={{status.HTTP_404_NOT_FOUND: {{"message": "ruta no encontrada"}}}}
)

@router.post("/", response_model={module_class_name}Read, status_code=status.HTTP_201_CREATED)
async def routes_post_{module_name}({module_name}: {module_class_name}Create, db: Session = Depends(get_db)):
    if {field_validations}:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        {module_name}_model = {module_class_name}Model(**{module_name}.model_dump())
        db_{module_name} = create_{module_name}(db=db, {module_name}={module_name}_model)
        return {module_class_name}Read.model_validate(db_{module_name})
    except Exception as e:
        logger.error(f"Error al crear {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{{{primary_key}}}", response_model={module_class_name}Read)
async def routes_get_{module_name}_{primary_key}({primary_key}: {primary_key_type}, db: Session = Depends(get_db)):
    try:
        db_{module_name} = get_{module_name}(db, {primary_key})
        if not db_{module_name}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: {module_name} no encontrado")
        return {module_class_name}Read.model_validate(db_{module_name})
    except Exception as e:
        logger.error(f"Error al obtener {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[{module_class_name}Read])
async def routes_gets_{module_name}_all(db: Session = Depends(get_db)):
    try:
        db_{module_name} = gets_{module_name}(db)
        if not db_{module_name}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: {module_name}s no encontrados")
        return [{module_class_name}Read.model_validate({module_name}) for {module_name} in db_{module_name}]
    except Exception as e:
        logger.error(f"Error al obtener registros de {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{{{primary_key}}}", response_model={module_class_name}Read)
async def routes_delete_{module_name}_numero({primary_key}: {primary_key_type}, db: Session = Depends(get_db)):
    try:
        resultado_{module_name} = get_{module_name}(db, {primary_key})
        if not resultado_{module_name}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: {module_name} no encontrado")
        db_{module_name} = delete_{module_name}(db, {primary_key})
        return {module_class_name}Read.model_validate(db_{module_name})
    except Exception as e:
        logger.error(f"Error al eliminar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{{{primary_key}}}", response_model={module_class_name}Read)
async def routes_update_{module_name}({primary_key}: {primary_key_type}, {module_name}: {module_class_name}Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando {module_class_name} con {primary_key} = {{{primary_key}}}")
    try:
        {module_name}_data = {module_name}.model_dump()
        db_{module_name} = update_{module_name}(db=db, {primary_key}={primary_key}, {module_name}_data={module_name}_data)
        return {module_class_name}Read.model_validate(db_{module_name})
    except Exception as e:
        logger.error(f"Error al actualizar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"sql_app/static/{module_name}/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
"""
    return route_code