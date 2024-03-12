from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ...schemas.Maestro.Usuarios import UsuarioCreate


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_usuario(db: Session, nombre: str, usuario: str, clave: str, email: str):
    try:
        # Encriptar la contraseña antes de guardarla
        clave_encriptada = pwd_context.hash(clave)
        sql = text("""INSERT INTO Usuarios (
                                codigo, Usuario, NombreCompleto, Clave, Email,Sucursal)
                                OUTPUT INSERTED.codigo AS codigo, INSERTED.Usuario AS Usuario, INSERTED.NombreCompleto AS Nombre, INSERTED.Email AS Email
                                VALUES (COALESCE((SELECT MAX(codigo) FROM Usuarios), 0) + 1, :usuario, :nombre, :clave, :email, (SELECT TOP 1 Sucursal FROM sistema GROUP BY Sucursal))""")
        result = db.execute(sql, {"usuario": usuario, "nombre": nombre, "clave": clave_encriptada, "email": email})
        rows = result.fetchall()
        db.commit()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="=( No se pudo crear el usuario")
    
  
def get_usuario(db: Session, codigo: int = None, usuario: str = None):
    print(codigo, usuario)
    try:
        if codigo is not None:
            result = db.execute(text("SELECT codigo,usuario,nombreCompleto,Email FROM Usuarios WHERE codigo = :codigo"), {"codigo": codigo})
            
        elif usuario is not None:
            result = db.execute(text("SELECT codigo,usuario,nombreCompleto,Email FROM Usuarios WHERE usuario = :usuario"), {"usuario": usuario})
        else:
            # Ambos parámetros no pueden ser nulos
            raise HTTPException(status_code=400, detail="Se debe proporcionar código o usuario para la búsqueda")
        rows = result.fetchall()
        if not rows:
            return None
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Usuario")

def gets_usuarios(db: Session):
    try:
        result = db.execute(text("SELECT codigo,usuario,nombreCompleto,Email FROM Usuarios"))
        Modelos = result.fetchall()
        if not Modelos:
            raise HTTPException(status_code=404, detail="No se encontraron Usuarios")
        return Modelos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudieron obtener Usuarios")
    

def delete_usuario(db: Session, codigo: int):
    try:
        statement = text("DELETE FROM Usuarios WHERE codigo = :codigo")
        db.execute(statement.params(codigo=codigo))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")
    

from sqlalchemy import text  # Add missing import statement

def update_usuario(db: Session, codigo: int, usuario: str, clave: str, nombre: str, email: str):
    try:
        clave_encriptada = pwd_context.hash(clave)
        result = db.execute(text("""UPDATE Usuarios SET Usuario = :usuario, Clave = :clave, NombreCompleto = :nombre, Email = :email 
                                    OUTPUT INSERTED.Codigo,INSERTED.Usuario, INSERTED.NombreCompleto, INSERTED.Email
                                    WHERE Codigo = :codigo"""), 
                           {"codigo": codigo, "usuario": usuario, "clave": clave_encriptada, "nombre": nombre, "email": email})
        rows = result.fetchall()
        db.commit()

        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]  # Return updated data

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
    
    
def authenticate_user(db: Session, username: str, password: str):
    if not password:
        return False
    result = db.execute(text("SELECT clave FROM Usuarios WHERE usuario = :usuario"), {"usuario": username})
    row = result.fetchone()
    if not row:
        return False
    hashed_password = row[0]  # Extrae la contraseña encriptada del objeto Row
    # Comprueba si la contraseña está encriptada
    if hashed_password and pwd_context.identify(hashed_password):
        if not pwd_context.verify(password, hashed_password):
            return False
    else:
        # Si la contraseña no está encriptada, compara directamente
        if password != hashed_password:
            return False
    return {"username": username}
