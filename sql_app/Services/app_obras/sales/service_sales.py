# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

# Imports del proyecto
from .model_sales import Sales
from .schema_sales import SalesCreate, SalesUpdate

import logging

logger = logging.getLogger(__name__)

def create_sales(db: Session, sales: Sales):
    """Crear una nueva venta"""
    try:
        db.add(sales)
        db.commit()
        db.refresh(sales)
        return sales
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear venta: {e}")
        raise e

def get_sales(db: Session, sales_id: int):
    """Obtener una venta por ID"""
    try:
        return db.query(Sales).filter(Sales.id == sales_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener venta: {e}")
        raise e

def get_all_sales(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las ventas con paginación"""
    try:
        return db.query(Sales).order_by(Sales.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de ventas: {e}")
        raise e

def get_sales_by_artwork(db: Session, artwork_id: int):
    """Obtener ventas por obra de arte"""
    try:
        return db.query(Sales).filter(Sales.artwork_id == artwork_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ventas por obra: {e}")
        raise e

def get_sales_by_year(db: Session, year: int):
    """Obtener ventas por año"""
    try:
        return db.query(Sales).filter(Sales.sale_year == year).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ventas por año: {e}")
        raise e

def get_sales_by_gallery(db: Session, gallery: str):
    """Obtener ventas por galería"""
    try:
        return db.query(Sales).filter(Sales.gallery.ilike(f"%{gallery}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ventas por galería: {e}")
        raise e

def get_sales_by_payment_status(db: Session, payment_status: str):
    """Obtener ventas por estado de pago"""
    try:
        return db.query(Sales).filter(Sales.payment_status == payment_status).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ventas por estado de pago: {e}")
        raise e

def get_pending_payments(db: Session):
    """Obtener ventas con pagos pendientes"""
    try:
        return db.query(Sales).filter(Sales.pending_amount > 0).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener pagos pendientes: {e}")
        raise e

def update_sales(db: Session, sales_id: int, sales_update: SalesUpdate):
    """Actualizar una venta"""
    try:
        db_sales = db.query(Sales).filter(Sales.id == sales_id).first()
        if not db_sales:
            return None
        
        update_data = sales_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sales, field, value)
        
        db.commit()
        db.refresh(db_sales)
        return db_sales
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar venta: {e}")
        raise e

def delete_sales(db: Session, sales_id: int):
    """Eliminar una venta"""
    try:
        db_sales = db.query(Sales).filter(Sales.id == sales_id).first()
        if not db_sales:
            return False
        
        db.delete(db_sales)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar venta: {e}")
        raise e

def calculate_artist_earnings(db: Session, artwork_id: int):
    """Calcular ganancias del artista para una obra"""
    try:
        sales = get_sales_by_artwork(db, artwork_id)
        total_earnings = Decimal('0.00')
        
        for sale in sales:
            if sale.payment_status == "Pagado":
                artist_share = sale.real_value * (sale.artist_share_percent / 100)
                total_earnings += artist_share
        
        return total_earnings
    except SQLAlchemyError as e:
        logger.error(f"Error al calcular ganancias del artista: {e}")
        raise e

def get_sales_summary_by_year(db: Session, year: int):
    """Obtener resumen de ventas por año"""
    try:
        sales = get_sales_by_year(db, year)
        
        total_sales = len(sales)
        total_value = sum(sale.real_value for sale in sales)
        paid_sales = [sale for sale in sales if sale.payment_status == "Pagado"]
        pending_amount = sum(sale.pending_amount for sale in sales)
        
        return {
            "year": year,
            "total_sales": total_sales,
            "total_value": total_value,
            "paid_sales": len(paid_sales),
            "pending_amount": pending_amount
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener resumen de ventas: {e}")
        raise e
