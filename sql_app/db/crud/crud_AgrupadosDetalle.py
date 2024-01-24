from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.AgrupadosDetalle import AgrupadosdetalleCreate

def create(db: Session, AgrupadosDetalle: AgrupadosdetalleCreate):
    try:
        sql = text("INSERT INTO AgrupadosDetalle(Grupo, Codigo) VALUES(:Grupo, :Codigo)")
        db.execute(sql.params(AgrupadosDetalle=AgrupadosDetalle))
        db.commit()
        result = db.execute(text("SELECT Grupo, Codigo FROM AgrupadosDetalle WHERE Grupo = :Grupo"), {"Grupo": AgrupadosDetalle.Grupo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el AgrupadosDetalle")

def get(db: Session, Grupo: INTEGER):
    try:
        result = db.execute(text("SELECT Grupo, Codigo FROM AgrupadosDetalle WHERE Grupo = :Grupo"), {"Grupo": Grupo})
        AgrupadosDetalle = result.fetchall()
        if AgrupadosDetalle is None:
            raise HTTPException(status_code=404, detail="Agrupadosdetalle no encontrado")
        return AgrupadosDetalle
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el AgrupadosDetalle")
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

