# ============================================================================
# OPERACIONES RELACIONADAS: ECOMMERCE_APP
# ============================================================================
"""
Operaciones especializadas para queries con múltiples tablas relacionadas
Servicio: ecommerce_app
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..ecommerce_app_models import *

class Ecommerce_AppRelationOperations:
    """Operaciones que involucran múltiples tablas relacionadas"""
    

    def get_usuarios_with_ordenes(self, db: Session, id: int) -> Optional[Usuarios]:
        """Obtener usuarios con todos sus ordenes"""
        return db.query(Usuarios).options(
            joinedload(Usuarios.ordenes)
        ).filter(Usuarios.id == id).first()
    
    def get_ordenes_by_usuarios(self, db: Session, id: int) -> List[Ordenes]:
        """Obtener todos los ordenes de un usuarios específico"""
        return db.query(Ordenes).filter(Ordenes.usuario_id == id).all()

    def get_ordenes_with_detalles(self, db: Session, id: int) -> Optional[Ordenes]:
        """Obtener ordenes con todos sus detalles"""
        return db.query(Ordenes).options(
            joinedload(Ordenes.detalles)
        ).filter(Ordenes.id == id).first()
    
    def get_detalles_by_ordenes(self, db: Session, id: int) -> List[DetalleOrden]:
        """Obtener todos los detalles de un ordenes específico"""
        return db.query(DetalleOrden).filter(DetalleOrden.orden_id == id).all()

    def get_productos_with_detalles_producto(self, db: Session, id: int) -> Optional[Productos]:
        """Obtener productos con todos sus detalles_producto"""
        return db.query(Productos).options(
            joinedload(Productos.detalles_producto)
        ).filter(Productos.id == id).first()
    
    def get_detalles_producto_by_productos(self, db: Session, id: int) -> List[DetalleOrden]:
        """Obtener todos los detalles_producto de un productos específico"""
        return db.query(DetalleOrden).filter(DetalleOrden.producto_id == id).all()

# Instancia global
ecommerce_app_relations = Ecommerce_AppRelationOperations()
