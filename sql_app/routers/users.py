from fastapi import APIRouter, HTTPException, status, Depends
from ..db.schemas.user import UserCreate, User
from sqlalchemy.orm import Session
from ..db.crud.users import get_users, get_user, get_user_by_email, create_user, delete_user, update_user
from ..db.database import  get_db


router = APIRouter(prefix="/userdb", 
                   tags=["Usuarios"], 
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No Encontrado"}})

# Rutas de la API hay  sacarlas fuera del main. 

@router.post("/users/", response_model=User)
def crea_user(user: UserCreate, db: Session = Depends(get_db)): 
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.get("/users/", response_model=list[User])
def read(db: Session = Depends(get_db)): 
    users = get_users(db)
    return users

@router.delete("/users/{user_id}", response_model=User)
def delete(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id) 
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db=db, user_id=user_id)
    return db_user


@router.put("/users/{user_id}", response_model=User)
def update(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user(db=db, user_id=user_id, user=user)
    return updated_user