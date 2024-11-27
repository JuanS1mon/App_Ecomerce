from pydantic import BaseModel, ConfigDict

class ProductsBase(BaseModel):
    name: str
    sku: str
    barcode: float
    quantity: str
    category: str
    location: str
    minimunstock: float
    maximumstock: float
    price: float
    cost: float
    supplier: str
    brand: str
    lastupdate: str

class ProductsCreate(ProductsBase):
    id: int

class ProductsUpdate(ProductsBase):
    pass

class ProductsRead(ProductsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
