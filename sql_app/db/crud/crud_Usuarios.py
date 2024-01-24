from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ..schemas.Usuarios import UsuariosCreate

def create(db: Session, Usuarios: UsuariosCreate):
    try:
        sql = text("INSERT INTO Usuarios(Codigo, Usuario, Clave, NombreCompleto, Sector, EMail, EstablecePermisos, Direccion, Telefono, Interno, DNI, Habilitado, Transmitido, EsVendedor, EsCobrador, EsRepartidor, EsCajero, PorcComisionCobranza, PorcComisionVenta, Nivel, HabilControl, Legajo, Sucursal, DuracionJornada) VALUES(:Codigo, :Usuario, :Clave, :NombreCompleto, :Sector, :EMail, :EstablecePermisos, :Direccion, :Telefono, :Interno, :DNI, :Habilitado, :Transmitido, :EsVendedor, :EsCobrador, :EsRepartidor, :EsCajero, :PorcComisionCobranza, :PorcComisionVenta, :Nivel, :HabilControl, :Legajo, :Sucursal, :DuracionJornada)")
        db.execute(sql.params(Usuarios=Usuarios))
        db.commit()
        result = db.execute(text("SELECT Codigo, Usuario, Clave, NombreCompleto, Sector, EMail, EstablecePermisos, Direccion, Telefono, Interno, DNI, Habilitado, Transmitido, EsVendedor, EsCobrador, EsRepartidor, EsCajero, PorcComisionCobranza, PorcComisionVenta, Nivel, HabilControl, Legajo, Sucursal, DuracionJornada FROM Usuarios WHERE Codigo = :Codigo"), {"Codigo": Usuarios.Codigo})
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="No se pudo crear el Usuarios")

def get(db: Session, Codigo: INTEGER):
    try:
        result = db.execute(text("SELECT Codigo, Usuario, Clave, NombreCompleto, Sector, EMail, EstablecePermisos, Direccion, Telefono, Interno, DNI, Habilitado, Transmitido, EsVendedor, EsCobrador, EsRepartidor, EsCajero, PorcComisionCobranza, PorcComisionVenta, Nivel, HabilControl, Legajo, Sucursal, DuracionJornada FROM Usuarios WHERE Codigo = :Codigo"), {"Codigo": Codigo})
        Usuarios = result.fetchall()
        if Usuarios is None:
            raise HTTPException(status_code=404, detail="Usuarios no encontrado")
        return Usuarios
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Usuarios")
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

