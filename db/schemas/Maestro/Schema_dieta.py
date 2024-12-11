from pydantic import BaseModel, ConfigDict

class DietaBase(BaseModel):
    comida: str
    fecha: str
    categoria: str
    dia: str

class DietaCreate(DietaBase):
    id: int

class DietaUpdate(DietaBase):
    pass

class DietaRead(DietaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
