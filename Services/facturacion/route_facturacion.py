
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
try:
    from ...db.database import get_db
except ImportError:
    from sql_app.db.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/facturacion",
    tags=["facturacion"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=FacturacionRead, status_code=status.HTTP_201_CREATED)
async def routes_post_facturacion(facturacion: FacturacionCreate, db: Session = Depends(get_db)):
    if facturacion.id is None or facturacion.nrofactura is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        facturacion_model = FacturacionModel(**facturacion.model_dump())
        db_facturacion = create_facturacion(db=db, facturacion=facturacion_model)
        return FacturacionRead.model_validate(db_facturacion)
    except Exception as e:
        logger.error(f"Error al crear Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=FacturacionRead)
async def routes_get_facturacion_id(id: int, db: Session = Depends(get_db)):
    try:
        db_facturacion = get_facturacion(db, id)
        if not db_facturacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: facturacion no encontrado")
        return FacturacionRead.model_validate(db_facturacion)
    except Exception as e:
        logger.error(f"Error al obtener Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[FacturacionRead])
async def routes_gets_facturacion_all(db: Session = Depends(get_db)):
    try:
        db_facturacion = gets_facturacion(db)
        if not db_facturacion:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: facturacions no encontrados")
        return [FacturacionRead.model_validate(facturacion) for facturacion in db_facturacion]
    except Exception as e:
        logger.error(f"Error al obtener registros de Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=FacturacionRead)
async def routes_delete_facturacion_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_facturacion = get_facturacion(db, id)
        if not resultado_facturacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: facturacion no encontrado")
        db_facturacion = delete_facturacion(db, id)
        return FacturacionRead.model_validate(db_facturacion)
    except Exception as e:
        logger.error(f"Error al eliminar Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=FacturacionRead)
async def routes_update_facturacion(id: int, facturacion: FacturacionUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Facturacion con id = {id}")
    try:
        facturacion_data = facturacion.model_dump()
        db_facturacion = update_facturacion(db=db, id=id, facturacion_data=facturacion_data)
        return FacturacionRead.model_validate(db_facturacion)
    except Exception as e:
        logger.error(f"Error al actualizar Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"sql_app/static/facturacion/crear_factura.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
