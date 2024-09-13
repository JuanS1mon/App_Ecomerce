from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

def create_Usuarios_roles(db: Session, id: int, usuario_id: int, empresa_id: int, rol: str, created_at: str, updated_at: str):
    try:
        sql = text("""INSERT INTO Usuarios_roles (id, usuario_id, empresa_id, rol, created_at, updated_at)
OUTPUT INSERTED.id AS id, INSERTED.usuario_id AS usuario_id, INSERTED.empresa_id AS empresa_id, INSERTED.rol AS rol, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
VALUES (COALESCE((SELECT MAX(id) FROM Usuarios_roles), 0) + 1, :usuario_id, :empresa_id, :rol, :created_at, :updated_at)""")
        sql = db.execute(sql.params(id=id, usuario_id=usuario_id, empresa_id=empresa_id, rol=rol, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'usuario_id': row[1], 'empresa_id': row[2], 'rol': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="SQL: No se pudo guardar registro en Usuarios_roles, intentelo de nuevo")

def get_Usuarios_roles(db: Session, id: int):
    try:
        if id is not None:
            query = text("SELECT id, usuario_id, empresa_id, rol, created_at, updated_at FROM Usuarios_roles WHERE id = :id")
            sql = db.execute(query.params(id=id))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuarios_roles no encontrado")
        result = sql.fetchall()
        return [{'id': row[0], 'usuario_id': row[1], 'empresa_id': row[2], 'rol': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de Usuarios_roles, intentelo de nuevo")

def gets_Usuarios_roles(db: Session):
    try:
        query = text("SELECT id, usuario_id, empresa_id, rol, created_at, updated_at FROM Usuarios_roles")
        sql = db.execute(query)
        result = sql.fetchall()
        return [{'id': row[0], 'usuario_id': row[1], 'empresa_id': row[2], 'rol': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de Usuarios_roles, intentelo de nuevo")

def delete_Usuarios_roles(db: Session, id: int):
    try:
        query = text("""DELETE FROM Usuarios_roles
 OUTPUT DELETED.id AS id, DELETED.usuario_id AS usuario_id, DELETED.empresa_id AS empresa_id, DELETED.rol AS rol, DELETED.created_at AS created_at, DELETED.updated_at AS updated_at WHERE id = :id  """)
        sql = db.execute(query.params(id=id))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'usuario_id': row[1], 'empresa_id': row[2], 'rol': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")

def get_Usuarios_roles_usuario_id(db: Session, usuario_id: str):
    try:
        if usuario_id is not None:
            query = text("SELECT id, usuario_id, empresa_id, rol, created_at, updated_at FROM Usuarios_roles WHERE usuario_id LIKE :usuario_id")
            sql = db.execute(query.params(usuario_id='%' + usuario_id + '%'))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuarios_roles no encontrado")
        result = sql.fetchall()
        if not result:
            return None
        return [{'id': row[0], 'usuario_id': row[1], 'empresa_id': row[2], 'rol': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

def update_Usuarios_roles(db: Session, id: int, usuario_id: int, empresa_id: int, rol: str, created_at: str, updated_at: str):
    try:
        query = text("""UPDATE Usuarios_roles SET usuario_id = :usuario_id, empresa_id = :empresa_id, rol = :rol, created_at = :created_at, updated_at = :updated_at
OUTPUT INSERTED.id AS id, INSERTED.usuario_id AS usuario_id, INSERTED.empresa_id AS empresa_id, INSERTED.rol AS rol, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
WHERE id = :id""")
        sql = db.execute(query.params(id=id, usuario_id=usuario_id, empresa_id=empresa_id, rol=rol, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'usuario_id': row[1], 'empresa_id': row[2], 'rol': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f" Route: descripcion no se pudo actualizar el codigo {codigo} en Familias ")

