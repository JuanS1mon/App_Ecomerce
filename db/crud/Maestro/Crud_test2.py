from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from ...models.test2 import test2

def create_test2(db: Session, campo1: int, campo2: str, campo3: float):
    try:
        new_record = test2(campo1=campo1, campo2=campo2, campo3=campo3)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_test2(db: Session, campo1: int):
    try:
        record = db.query(test2).filter(test2.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test2 no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def gets_test2(db: Session):
    try:
        records = db.query(test2).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_test2(db: Session, campo1: int):
    try:
        record = db.query(test2).filter(test2.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test2 no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def update_test2(db: Session, campo1: int, campo2: str, campo3: float):
    try:
        record = db.query(test2).filter(test2.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test2 no encontrado")
        for key, value in locals().items():
            if key in ['campo1', 'campo2', 'campo3'] and value is not None:
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

