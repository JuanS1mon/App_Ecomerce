# Imports de bibliotecas estándar
from decimal import Decimal
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class SalesBase(BaseModel):
    artwork_id: int
    sale_year: int
    gallery: str
    buyer_collection: str
    buyer_mention: Optional[str] = None
    location_id: int
    intermediary: Optional[str] = None
    provenance: Optional[str] = None
    list_value: Decimal
    real_value: Decimal
    artist_share_percent: Decimal
    payment_status: str
    pending_amount: Decimal = Decimal('0.00')

class SalesCreate(SalesBase):
    id: Optional[int] = None

class SalesUpdate(BaseModel):
    artwork_id: Optional[int] = None
    sale_year: Optional[int] = None
    gallery: Optional[str] = None
    buyer_collection: Optional[str] = None
    buyer_mention: Optional[str] = None
    location_id: Optional[int] = None
    intermediary: Optional[str] = None
    provenance: Optional[str] = None
    list_value: Optional[Decimal] = None
    real_value: Optional[Decimal] = None
    artist_share_percent: Optional[Decimal] = None
    payment_status: Optional[str] = None
    pending_amount: Optional[Decimal] = None

class SalesRead(SalesBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
