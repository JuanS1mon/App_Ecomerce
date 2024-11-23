from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from ...models.pruebe import pruebe

def create_pruebe(db: Session, campoq: int, campob: str, campoc: float):
    try:
        new_record = pruebe(campoq=campoq, campob=campob, campoc=campoc)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_pruebe(db: Session, campoq: int):
    try:
        record = db.query(pruebe).filter(pruebe.campoq == campoq).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pruebe no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def gets_pruebe(db: Session):
    try:
        records = db.query(pruebe).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_pruebe(db: Session, campoq: int):
    try:
        record = db.query(pruebe).filter(pruebe.campoq == campoq).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pruebe no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def update_pruebe(db: Session, campoq: int, campob: str, campoc: float):
    try:
        record = db.query(pruebe).filter(pruebe.campoq == campoq).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pruebe no encontrado")
        for key, value in locals().items():
            if key in ['campoq', 'campob', 'campoc'] and value is not None:
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

