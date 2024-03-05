from pydantic import BaseModel, Field # Importamos BaseModel de pydantic para crear modelos de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.


class MarcaBase(BaseModel):
    codigo: int 
    description: str


class MarcaCreate(BaseModel):
    descripcion: str


class Marca(BaseModel):
    codigo: int
    descripcion: str

    #class Config: 
        #from_attributes = True
