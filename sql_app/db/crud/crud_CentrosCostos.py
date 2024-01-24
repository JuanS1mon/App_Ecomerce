from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.CentrosCostos import CentroscostosCreate

def create(db: Session, CentrosCostos: CentroscostosCreate):
    try:
        sql = text("INSERT INTO CentrosCostos(Codigo, Descripcion, Transmitido) VALUES(:Codigo, :Descripcion, :Transmitido)")
        db.execute(sql.params(CentrosCostos=CentrosCostos))
        db.commit()
        result = db.execute(text("SELECT Codigo, Descripcion, Transmitido FROM CentrosCostos WHERE Codigo = :Codigo"), {"Codigo": CentrosCostos.Codigo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el CentrosCostos")

def get(db: Session, Codigo: INTEGER):
    try:
        result = db.execute(text("SELECT Codigo, Descripcion, Transmitido FROM CentrosCostos WHERE Codigo = :Codigo"), {"Codigo": Codigo})
        CentrosCostos = result.fetchall()
        if CentrosCostos is None:
            raise HTTPException(status_code=404, detail="Centroscostos no encontrado")
        return CentrosCostos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el CentrosCostos")
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

