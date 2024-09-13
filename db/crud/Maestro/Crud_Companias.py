from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

def create_Companias(db: Session, id: int, nombre: str, direccion: str, telefono: str, created_at: str, updated_at: str):
    try:
        sql = text("""INSERT INTO Companias (id, nombre, direccion, telefono, created_at, updated_at)
OUTPUT INSERTED.id AS id, INSERTED.nombre AS nombre, INSERTED.direccion AS direccion, INSERTED.telefono AS telefono, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
VALUES (COALESCE((SELECT MAX(id) FROM Companias), 0) + 1, :nombre, :direccion, :telefono, :created_at, :updated_at)""")
        sql = db.execute(sql.params(id=id, nombre=nombre, direccion=direccion, telefono=telefono, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="SQL: No se pudo guardar registro en Companias, intentelo de nuevo")

def get_Companias(db: Session, id: int):
    try:
        if id is not None:
            query = text("SELECT id, nombre, direccion, telefono, created_at, updated_at FROM Companias WHERE id = :id")
            sql = db.execute(query.params(id=id))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Companias no encontrado")
        result = sql.fetchall()
        return [{'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de Companias, intentelo de nuevo")

def gets_Companias(db: Session):
    try:
        query = text("SELECT id, nombre, direccion, telefono, created_at, updated_at FROM Companias")
        sql = db.execute(query)
        result = sql.fetchall()
        return [{'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de Companias, intentelo de nuevo")

def delete_Companias(db: Session, id: int):
    try:
        query = text("""DELETE FROM Companias
 OUTPUT DELETED.id AS id, DELETED.nombre AS nombre, DELETED.direccion AS direccion, DELETED.telefono AS telefono, DELETED.created_at AS created_at, DELETED.updated_at AS updated_at WHERE id = :id  """)
        sql = db.execute(query.params(id=id))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")

def get_Companias_nombre(db: Session, nombre: str):
    try:
        if nombre is not None:
            query = text("SELECT id, nombre, direccion, telefono, created_at, updated_at FROM Companias WHERE nombre LIKE :nombre")
            sql = db.execute(query.params(nombre='%' + nombre + '%'))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Companias no encontrado")
        result = sql.fetchall()
        if not result:
            return None
        return [{'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

def update_Companias(db: Session, id: int, nombre: str, direccion: str, telefono: str, created_at: str, updated_at: str):
    try:
        query = text("""UPDATE Companias SET nombre = :nombre, direccion = :direccion, telefono = :telefono, created_at = :created_at, updated_at = :updated_at
OUTPUT INSERTED.id AS id, INSERTED.nombre AS nombre, INSERTED.direccion AS direccion, INSERTED.telefono AS telefono, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
WHERE id = :id""")
        sql = db.execute(query.params(id=id, nombre=nombre, direccion=direccion, telefono=telefono, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f" Route: descripcion no se pudo actualizar el codigo {codigo} en Familias ")

