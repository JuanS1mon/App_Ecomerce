from pydantic import BaseModel # Importamos BaseModel de pydantic para crear modelos de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.

class Modulos(BaseModel):
    descripcion: str 
    ejecutable: str
    class Config:
        from_attributes = True