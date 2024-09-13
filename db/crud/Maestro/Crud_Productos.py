from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

def create_Productos(db: Session, id: int, nombre: str, descripcion: str, precio: float, stock_cantidad: float, Id_compania: int, created_at: str, updated_at: str):
    try:
        sql = text("""INSERT INTO Productos (id, nombre, descripcion, precio, stock_cantidad, Id_compania, created_at, updated_at)
OUTPUT INSERTED.id AS id, INSERTED.nombre AS nombre, INSERTED.descripcion AS descripcion, INSERTED.precio AS precio, INSERTED.stock_cantidad AS stock_cantidad, INSERTED.Id_compania AS Id_compania, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
VALUES (COALESCE((SELECT MAX(id) FROM Productos), 0) + 1, :nombre, :descripcion, :precio, :stock_cantidad, :Id_compania, :created_at, :updated_at)""")
        sql = db.execute(sql.params(id=id, nombre=nombre, descripcion=descripcion, precio=precio, stock_cantidad=stock_cantidad, Id_compania=Id_compania, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'precio': row[3], 'stock_cantidad': row[4], 'Id_compania': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="SQL: No se pudo guardar registro en Productos, intentelo de nuevo")

def get_Productos(db: Session, id: int):
    try:
        if id is not None:
            query = text("SELECT id, nombre, descripcion, precio, stock_cantidad, Id_compania, created_at, updated_at FROM Productos WHERE id = :id")
            sql = db.execute(query.params(id=id))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Productos no encontrado")
        result = sql.fetchall()
        return [{'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'precio': row[3], 'stock_cantidad': row[4], 'Id_compania': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de Productos, intentelo de nuevo")

def gets_Productos(db: Session):
    try:
        query = text("SELECT id, nombre, descripcion, precio, stock_cantidad, Id_compania, created_at, updated_at FROM Productos")
        sql = db.execute(query)
        result = sql.fetchall()
        return [{'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'precio': row[3], 'stock_cantidad': row[4], 'Id_compania': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de Productos, intentelo de nuevo")

def delete_Productos(db: Session, id: int):
    try:
        query = text("""DELETE FROM Productos
 OUTPUT DELETED.id AS id, DELETED.nombre AS nombre, DELETED.descripcion AS descripcion, DELETED.precio AS precio, DELETED.stock_cantidad AS stock_cantidad, DELETED.Id_compania AS Id_compania, DELETED.created_at AS created_at, DELETED.updated_at AS updated_at WHERE id = :id  """)
        sql = db.execute(query.params(id=id))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'precio': row[3], 'stock_cantidad': row[4], 'Id_compania': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")

def get_Productos_nombre(db: Session, nombre: str):
    try:
        if nombre is not None:
            query = text("SELECT id, nombre, descripcion, precio, stock_cantidad, Id_compania, created_at, updated_at FROM Productos WHERE nombre LIKE :nombre")
            sql = db.execute(query.params(nombre='%' + nombre + '%'))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Productos no encontrado")
        result = sql.fetchall()
        if not result:
            return None
        return [{'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'precio': row[3], 'stock_cantidad': row[4], 'Id_compania': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

def update_Productos(db: Session, id: int, nombre: str, descripcion: str, precio: float, stock_cantidad: float, Id_compania: int, created_at: str, updated_at: str):
    try:
        query = text("""UPDATE Productos SET nombre = :nombre, descripcion = :descripcion, precio = :precio, stock_cantidad = :stock_cantidad, Id_compania = :Id_compania, created_at = :created_at, updated_at = :updated_at
OUTPUT INSERTED.id AS id, INSERTED.nombre AS nombre, INSERTED.descripcion AS descripcion, INSERTED.precio AS precio, INSERTED.stock_cantidad AS stock_cantidad, INSERTED.Id_compania AS Id_compania, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
WHERE id = :id""")
        sql = db.execute(query.params(id=id, nombre=nombre, descripcion=descripcion, precio=precio, stock_cantidad=stock_cantidad, Id_compania=Id_compania, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'precio': row[3], 'stock_cantidad': row[4], 'Id_compania': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f" Route: descripcion no se pudo actualizar el codigo {codigo} en Familias ")

