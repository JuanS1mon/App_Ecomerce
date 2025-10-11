# Imports de bibliotecas estándar
from typing import List

# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Imports del proyecto
from Services.security.security import require_admin
from sql_app.db.crud.config.roles import get_role_by_name, create_role, delete_role, get_all_roles
from db.database import get_db
from db.schemas.config.roles import Role, RoleAssignment, RoleCreate

router = APIRouter(
    prefix="/admin/roles",
    tags=["Roles"],
    dependencies=[Depends(require_admin)]  # Solo admins pueden acceder
)

@router.get("/", response_model=List[Role])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene todos los roles"""
    return get_all_roles(db, skip, limit)

@router.post("/", response_model=Role)
def create_new_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Crea un nuevo rol"""
    existing = get_role_by_name(db, role.nombre)
    if existing:
        raise HTTPException(status_code=400, detail=f"El rol '{role.nombre}' ya existe")
    return create_role(db, role.nombre, role.descripcion)

@router.delete("/{role_id}")
def delete_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    """Elimina un rol"""
    result = delete_role(db, role_id)
    if not result:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"status": "success", "message": "Rol eliminado correctamente"}

# TODO: Implementar las siguientes funcionalidades cuando estén disponibles las funciones CRUD:
# - assign_role_to_user
# - remove_role_from_user  
# - get_user_roles