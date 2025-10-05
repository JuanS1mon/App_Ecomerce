# ============================================================================
# SCHEMAS: PEDIDOS
# ============================================================================
"""
Schemas Pydantic para pedidos
Parte del servicio: pizzeria_one_man_company
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PedidosBase(BaseModel):
    """Schema base para pedidos"""
    id_usuario: int
    id_cliente: Optional[int] = None
    items_json: str
    subtotal: int
    descuento: Optional[int] = None
    total: int
    metodo_pago: str
    estado: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class PedidosCreate(PedidosBase):
    """Schema para crear pedidos"""
    pass

class PedidosUpdate(PedidosBase):
    """Schema para actualizar pedidos"""
    pass

class PedidosInDB(PedidosBase):
    """Schema para pedidos en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_usuario: int
    id_cliente: Optional[int] = None
    items_json: str
    subtotal: int
    descuento: Optional[int] = None
    total: int
    metodo_pago: str
    estado: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Alias para compatibilidad
Pedidos = PedidosInDB
