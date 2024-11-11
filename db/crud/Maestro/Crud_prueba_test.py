from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from ...models.prueba_test import prueba_test

def create_prueba_test(db: Session, campo1: int, campostr: str, campofloat: float):
    try:
        new_record = prueba_test(campo1=campo1, campostr=campostr, campofloat=campofloat)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_prueba_test(db: Session, campo1: int):
    try:
        record = db.query(prueba_test).filter(prueba_test.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="prueba_test no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def gets_prueba_test(db: Session):
    try:
        records = db.query(prueba_test).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_prueba_test(db: Session, campo1: int):
    try:
        record = db.query(prueba_test).filter(prueba_test.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="prueba_test no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def update_prueba_test(db: Session, campo1: int, campostr: str, campofloat: float):
    try:
        record = db.query(prueba_test).filter(prueba_test.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="prueba_test no encontrado")
        for key, value in locals().items():
            if key in ['campo1', 'campostr', 'campofloat'] and value is not None:
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

