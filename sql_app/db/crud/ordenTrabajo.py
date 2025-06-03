from sqlalchemy.orm import Session
from sql_app.Services.app_stock.ot.OrdenTrabajo import OrdenTrabajo, Operacion, ReporteTiempo
from .ordenTrabajo import OrdenTrabajoCreate, OrdenTrabajoUpdate, OperacionCreate, OperacionUpdate, ReporteTiempoCreate, ReporteTiempoUpdate
from datetime import datetime
from typing import List, Optional
from sqlalchemy import desc

# Funciones CRUD para Órdenes de Trabajo
def get_orden_trabajo(db: Session, ot_id: int):
    return db.query(OrdenTrabajo).filter(OrdenTrabajo.id == ot_id).first()

def get_orden_trabajo_by_numero(db: Session, numero: str):
    return db.query(OrdenTrabajo).filter(OrdenTrabajo.numero == numero).first()

def get_ordenes_trabajo(db: Session, skip: int = 0, limit: int = 100, cliente_id: Optional[int] = None, 
                        estado: Optional[str] = None, tecnico_id: Optional[int] = None):
    query = db.query(OrdenTrabajo)
    
    if cliente_id:
        query = query.filter(OrdenTrabajo.cliente_id == cliente_id)
    if estado:
        query = query.filter(OrdenTrabajo.estado == estado)
    if tecnico_id:
        query = query.filter(OrdenTrabajo.tecnico_id == tecnico_id)
    
    return query.order_by(desc(OrdenTrabajo.fecha_creacion)).offset(skip).limit(limit).all()

def create_orden_trabajo(db: Session, ot: OrdenTrabajoCreate):
    db_ot = OrdenTrabajo(
        numero=ot.numero,
        cliente_id=ot.cliente_id,
        descripcion=ot.descripcion,
        fecha_entrega=ot.fecha_entrega,
        estado=ot.estado,
        prioridad=ot.prioridad,
        tecnico_id=ot.tecnico_id,
        notas=ot.notas,
        costo_total=ot.costo_total
    )
    db.add(db_ot)
    db.commit()
    db.refresh(db_ot)
    
    # Crear operaciones asociadas si se proporcionan
    if ot.operaciones:
        for op_data in ot.operaciones:
            db_op = Operacion(
                orden_trabajo_id=db_ot.id,
                descripcion=op_data.descripcion,
                tiempo_estimado=op_data.tiempo_estimado,
                estado=op_data.estado,
                costo=op_data.costo
            )
            db.add(db_op)
        db.commit()
        db.refresh(db_ot)
    
    return db_ot

def update_orden_trabajo(db: Session, ot_id: int, ot: OrdenTrabajoUpdate):
    db_ot = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == ot_id).first()
    if db_ot:
        update_data = ot.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ot, key, value)
        db.commit()
        db.refresh(db_ot)
    return db_ot

def delete_orden_trabajo(db: Session, ot_id: int):
    db_ot = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == ot_id).first()
    if db_ot:
        db.delete(db_ot)
        db.commit()
        return True
    return False

# Funciones CRUD para Operaciones
def get_operacion(db: Session, op_id: int):
    return db.query(Operacion).filter(Operacion.id == op_id).first()

def get_operaciones_by_ot(db: Session, ot_id: int):
    return db.query(Operacion).filter(Operacion.orden_trabajo_id == ot_id).all()

def create_operacion(db: Session, op: OperacionCreate, ot_id: int):
    db_op = Operacion(
        orden_trabajo_id=ot_id,
        descripcion=op.descripcion,
        tiempo_estimado=op.tiempo_estimado,
        estado=op.estado,
        costo=op.costo
    )
    db.add(db_op)
    db.commit()
    db.refresh(db_op)
    
    # Actualizar costo total de la OT
    update_costo_total_ot(db, ot_id)
    
    return db_op

def update_operacion(db: Session, op_id: int, op: OperacionUpdate):
    db_op = db.query(Operacion).filter(Operacion.id == op_id).first()
    if db_op:
        update_data = op.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_op, key, value)
        db.commit()
        db.refresh(db_op)
        
        # Actualizar costo total de la OT
        update_costo_total_ot(db, db_op.orden_trabajo_id)
        
    return db_op

def delete_operacion(db: Session, op_id: int):
    db_op = db.query(Operacion).filter(Operacion.id == op_id).first()
    if db_op:
        ot_id = db_op.orden_trabajo_id
        db.delete(db_op)
        db.commit()
        
        # Actualizar costo total de la OT
        update_costo_total_ot(db, ot_id)
        
        return True
    return False

# Funciones CRUD para Reportes de Tiempo
def get_reporte_tiempo(db: Session, reporte_id: int):
    return db.query(ReporteTiempo).filter(ReporteTiempo.id == reporte_id).first()

def get_reportes_tiempo_by_ot(db: Session, ot_id: int):
    return db.query(ReporteTiempo).filter(ReporteTiempo.orden_trabajo_id == ot_id).all()

def get_reportes_tiempo_by_tecnico(db: Session, tecnico_id: int):
    return db.query(ReporteTiempo).filter(ReporteTiempo.tecnico_id == tecnico_id).all()

def create_reporte_tiempo(db: Session, reporte: ReporteTiempoCreate, ot_id: int):
    db_reporte = ReporteTiempo(
        orden_trabajo_id=ot_id,
        tecnico_id=reporte.tecnico_id,
        fecha_inicio=reporte.fecha_inicio,
        fecha_fin=reporte.fecha_fin,
        descripcion=reporte.descripcion,
        duracion=reporte.duracion
    )
    db.add(db_reporte)
    db.commit()
    db.refresh(db_reporte)
    return db_reporte

def update_reporte_tiempo(db: Session, reporte_id: int, reporte: ReporteTiempoUpdate):
    db_reporte = db.query(ReporteTiempo).filter(ReporteTiempo.id == reporte_id).first()
    if db_reporte:
        update_data = reporte.dict(exclude_unset=True)
        
        # Si se proporciona fecha_fin, calcular automáticamente la duración
        if "fecha_fin" in update_data and update_data["fecha_fin"] and not "duracion" in update_data:
            delta = update_data["fecha_fin"] - db_reporte.fecha_inicio
            update_data["duracion"] = delta.total_seconds() / 3600  # Convertir a horas
        
        for key, value in update_data.items():
            setattr(db_reporte, key, value)
        db.commit()
        db.refresh(db_reporte)
    return db_reporte

def delete_reporte_tiempo(db: Session, reporte_id: int):
    db_reporte = db.query(ReporteTiempo).filter(ReporteTiempo.id == reporte_id).first()
    if db_reporte:
        db.delete(db_reporte)
        db.commit()
        return True
    return False

# Funciones auxiliares
def update_costo_total_ot(db: Session, ot_id: int):
    """Actualiza el costo total de una orden de trabajo basado en sus operaciones"""
    operaciones = db.query(Operacion).filter(Operacion.orden_trabajo_id == ot_id).all()
    costo_total = sum(op.costo for op in operaciones)
    
    db_ot = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == ot_id).first()
    if db_ot:
        db_ot.costo_total = costo_total
        db.commit()