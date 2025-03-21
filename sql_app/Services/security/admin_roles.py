from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.crud.config.roles import get_all_roles, create_role, get_role_by_name, delete_role
from db.crud.config.Usuarios import assign_role_to_user, remove_role_from_user, get_user_roles
from db.schemas.config.roles import Role, RoleCreate, RoleAssignment
from Services.security.security import require_admin
from typing import List

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

@router.post("/assign")
def assign_role(assignment: RoleAssignment, db: Session = Depends(get_db)):
    """Asigna un rol a un usuario"""
    result = assign_role_to_user(db, assignment.usuario_id, assignment.role_id)
    if not result:
        raise HTTPException(status_code=404, detail="Usuario o rol no encontrado")
    return {"status": "success", "message": "Rol asignado correctamente"}

@router.post("/remove")
def remove_role(assignment: RoleAssignment, db: Session = Depends(get_db)):
    """Elimina un rol de un usuario"""
    result = remove_role_from_user(db, assignment.usuario_id, assignment.role_id)
    if not result:
        raise HTTPException(status_code=404, detail="Usuario, rol o asignación no encontrada")
    return {"status": "success", "message": "Rol eliminado correctamente"}

@router.get("/user/{user_id}", response_model=List[Role])
def get_roles_for_user(user_id: int, db: Session = Depends(get_db)):
    """Obtiene todos los roles de un usuario"""
    return get_user_roles(db, user_id)

@router.delete("/{role_id}")
def delete_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    """Elimina un rol"""
    result = delete_role(db, role_id)
    if not result:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"status": "success", "message": "Rol eliminado correctamente"}