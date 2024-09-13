from pydantic import BaseModel, Field # Importamos BaseModel de pydantic para crear modelos de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.


class ModeloBase(BaseModel):
    codigo: int 
    description: str


class ModeloCreate(BaseModel):
    descripcion: str


class Modelo(BaseModel):
    codigo: int
    descripcion: str

    #class Config: 
        #from_attributes = True
