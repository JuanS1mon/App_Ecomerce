from pydantic import BaseModel # Importamos BaseModel de pydantic para crear modelos de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.


class UserBase(BaseModel):
    email: str
    hashed_password: str

class UserCreate(BaseModel):
    email: str
    hashed_password: str  # Cambie esto a una password encriptada o hasheada


class User(UserBase):
    email: str
    hashed_password: str