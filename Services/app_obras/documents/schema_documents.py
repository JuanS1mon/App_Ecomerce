# Imports de bibliotecas estándar
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class DocumentsBase(BaseModel):
    artwork_id: int
    doc_type: str
    url: str

class DocumentsCreate(DocumentsBase):
    id: Optional[int] = None

class DocumentsUpdate(BaseModel):
    artwork_id: Optional[int] = None
    doc_type: Optional[str] = None
    url: Optional[str] = None

class DocumentsRead(DocumentsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
