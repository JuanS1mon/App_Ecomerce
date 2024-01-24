from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.ArticulosDatosAdicionales import ArticulosdatosadicionalesCreate

def create(db: Session, ArticulosDatosAdicionales: ArticulosdatosadicionalesCreate):
    try:
        sql = text("INSERT INTO ArticulosDatosAdicionales(Campo, Dato, Articulo, FechaSincro) VALUES(:Campo, :Dato, :Articulo, :FechaSincro)")
        db.execute(sql.params(ArticulosDatosAdicionales=ArticulosDatosAdicionales))
        db.commit()
        result = db.execute(text("SELECT Campo, Dato, Articulo, FechaSincro FROM ArticulosDatosAdicionales WHERE Campo = :Campo"), {"Campo": ArticulosDatosAdicionales.Campo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el ArticulosDatosAdicionales")

def get(db: Session, Campo: NVARCHAR):
    try:
        result = db.execute(text("SELECT Campo, Dato, Articulo, FechaSincro FROM ArticulosDatosAdicionales WHERE Campo = :Campo"), {"Campo": Campo})
        ArticulosDatosAdicionales = result.fetchall()
        if ArticulosDatosAdicionales is None:
            raise HTTPException(status_code=404, detail="Articulosdatosadicionales no encontrado")
        return ArticulosDatosAdicionales
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el ArticulosDatosAdicionales")
def get_campo(db: Session, campo: str):
    try:
        result = db.execute(text("SELECT codigo FROM marcas WHERE descripcion = :campo"), {"campo": descripcion})
        marca = result.fetchone()
        if marca is None:
            return marca
        else:
            raise HTTPException(status_code=404, detail=f"Marca '{campo}', ya se encuentra registrada")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener la marca")

def gets(db: Session):
    try:
        result = db.execute(text("SELECT codigo,descripcion FROM marcas"))
        marcas = result.fetchall()
        if not marcas:
            raise HTTPException(status_code=404, detail="No se encontraron marcas")
        return marcas
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudieron obtener las marcas")

def update(db: Session, codigo: int, descripcion: str):
    try:
        db.execute(text("UPDATE marcas SET descripcion = :descripcion WHERE codigo = :codigo"), {"codigo": codigo, "descripcion": descripcion})
        db.commit()
        return get(db, codigo=codigo)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar la marca")

