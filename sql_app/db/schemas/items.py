from pydantic import BaseModel # Importamos BaseModel de pydantic para crear modelos de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.


class ItemBase(BaseModel):# ItemBase es un modelo de datos que se utilizará para validar la entrada de datos y convertir los datos en diferentes formatos.
    title: str # title es un atributo de ItemBase que representa una columna en la tabla de la base de datos.
    description: str | None = None # description es un atributo de ItemBase que representa una columna en la tabla de la base de datos.


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config: # Config es una clase interna de Pydantic que permite configurar los modelos.
        from_attributes = True# from_attributes=True le dice a Pydantic que cree un modelo basado en los atributos de la clase. Esto significa que los atributos de la clase Item se utilizarán para crear el modelo.
