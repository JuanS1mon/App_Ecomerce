from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Teclados import TecladosCreate

def create(db: Session, Teclados: TecladosCreate):
    try:
        sql = text("INSERT INTO Teclados(Teclado, Descripcion) VALUES(:Teclado, :Descripcion)")
        db.execute(sql.params(Teclados=Teclados))
        db.commit()
        result = db.execute(text("SELECT Teclado, Descripcion FROM Teclados WHERE Teclado = :Teclado"), {"Teclado": Teclados.Teclado})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Teclados")

def get(db: Session, Teclado: INTEGER):
    try:
        result = db.execute(text("SELECT Teclado, Descripcion FROM Teclados WHERE Teclado = :Teclado"), {"Teclado": Teclado})
        Teclados = result.fetchall()
        if Teclados is None:
            raise HTTPException(status_code=404, detail="Teclados no encontrado")
        return Teclados
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Teclados")
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

