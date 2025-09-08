# Imports de bibliotecas estándar
from Services.app_stock.ot.model_ot import OT, Operacion, ReporteTiempo# Configuración del logger
from datetime import datetime
from typing import List, Optional
import logging

# Imports de terceros
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Servicios para Órdenes de Trabajo (OT)
class OTService:
    @staticmethod
    def get_ots(db: Session, skip: int = 0, limit: int = 100):
        """Obtiene todas las OT ordenadas por ID descendente"""
        return db.query(OT).order_by(OT.id.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_ot_by_id(db: Session, ot_id: int):
        """Obtiene una OT por su ID"""
        return db.query(OT).filter(OT.id == ot_id).first()
    
    @staticmethod
    def get_ots_by_estado(db: Session, estado: str, skip: int = 0, limit: int = 100):
        """Obtiene OTs filtradas por estado"""
        return db.query(OT).filter(OT.estado == estado).order_by(OT.id.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_ots(db: Session, query: str, skip: int = 0, limit: int = 100):
        """Busca OTs por diferentes campos"""
        search = f"%{query}%"
        return db.query(OT).filter(
            or_(
                OT.id_trabajo.ilike(search),
                OT.titulo.ilike(search),
                OT.area.ilike(search),
                OT.personal.ilike(search),
                OT.descripcion.ilike(search)
            )
        ).order_by(OT.id.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_ot(db: Session, ot_data: OTCreate):
        """Crea una nueva OT"""
        db_ot = OT(**ot_data.dict())
        db.add(db_ot)
        db.commit()
        db.refresh(db_ot)
        return db_ot
    
    @staticmethod
    def update_ot(db: Session, ot_id: int, ot_data: OTUpdate):
        """Actualiza una OT existente"""
        db_ot = OTService.get_ot_by_id(db, ot_id)
        if not db_ot:
            return None
        
        update_data = ot_data.dict(exclude_unset=True)
        
        # Verificar si se cambió el estado a 'en_proceso'
        if 'estado' in update_data and update_data['estado'] == 'en_proceso' and db_ot.estado != 'en_proceso':
            update_data['fecha_inicio'] = datetime.utcnow()
        
        # Verificar si se cambió el estado a 'finalizada'
        if 'estado' in update_data and update_data['estado'] == 'finalizada' and db_ot.estado != 'finalizada':
            update_data['fecha_fin'] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(db_ot, key, value)
        
        db.commit()
        db.refresh(db_ot)
        return db_ot
    
    @staticmethod
    def delete_ot(db: Session, ot_id: int):
        """Elimina una OT por su ID"""
        db_ot = OTService.get_ot_by_id(db, ot_id)
        if not db_ot:
            return False
        
        db.delete(db_ot)
        db.commit()
        return True
    
    @staticmethod
    def finalizar_ot(db: Session, ot_id: int):
        """Finaliza una OT comprobando que todas sus operaciones estén finalizadas"""
        db_ot = OTService.get_ot_by_id(db, ot_id)
        if not db_ot:
            return None
        
        # Verificar si todas las operaciones están finalizadas
        operaciones = db_ot.operaciones
        if operaciones:
            for op in operaciones:
                if op.estado != 'finalizada':
                    return {"success": False, "message": f"No se puede finalizar la OT porque la operación '{op.descripcion}' no está finalizada"}
        
        # Cambiar estado y registrar fecha de finalización
        db_ot.estado = 'finalizada'
        db_ot.fecha_fin = datetime.utcnow()
        db.commit()
        db.refresh(db_ot)
        return {"success": True, "ot": db_ot}