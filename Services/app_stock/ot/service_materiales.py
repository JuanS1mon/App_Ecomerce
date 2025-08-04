# Imports de bibliotecas estándar
import datetime
import logging
from typing import List, Optional, Dict, Any

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

# Imports del proyecto
from .model_ot import OTMaterial, OT
from ..stock.model_stock import Stock as StockModel

logger = logging.getLogger(__name__)

# ===== CRUD de Materiales de OT =====

def create_ot_material(db: Session, material: OTMaterial) -> OTMaterial:
    """
    Crea un nuevo material planificado para una OT
    """
    try:
        db.add(material)
        db.commit()
        db.refresh(material)
        logger.info(f"Material creado para OT {material.ot_id}: {material.codigo_art}")
        return material
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear material de OT: {e}")
        raise

def get_ot_material(db: Session, material_id: int) -> Optional[OTMaterial]:
    """
    Obtiene un material específico por ID
    """
    return db.query(OTMaterial).filter(OTMaterial.id == material_id).first()

def get_materiales_by_ot(db: Session, ot_id: int) -> List[OTMaterial]:
    """
    Obtiene todos los materiales asociados a una OT
    """
    return db.query(OTMaterial).filter(OTMaterial.ot_id == ot_id).all()

def update_ot_material(db: Session, material_id: int, material_data: Dict[str, Any]) -> OTMaterial:
    """
    Actualiza un material de OT
    """
    try:
        material = get_ot_material(db, material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado")
        
        for key, value in material_data.items():
            if hasattr(material, key) and value is not None:
                setattr(material, key, value)
        
        db.commit()
        db.refresh(material)
        logger.info(f"Material {material_id} actualizado")
        return material
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar material: {e}")
        raise

def delete_ot_material(db: Session, material_id: int) -> OTMaterial:
    """
    Elimina un material de OT
    """
    try:
        material = get_ot_material(db, material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado")
        
        db.delete(material)
        db.commit()
        logger.info(f"Material {material_id} eliminado")
        return material
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar material: {e}")
        raise

# ===== Funciones de Negocio =====

def planificar_materiales_ot(db: Session, ot_id: int, materiales_data: List[Dict[str, Any]]) -> List[OTMaterial]:
    """
    Planifica múltiples materiales para una OT
    """
    try:
        # Verificar que la OT existe
        ot = db.query(OT).filter(OT.id == ot_id).first()
        if not ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OT no encontrada")
        
        # Verificar que la OT esté en estado válido para planificar materiales
        if ot.estado in ["finalizada", "cancelada"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se pueden planificar materiales en una OT finalizada o cancelada"
            )
        
        materiales_creados = []
        
        for material_data in materiales_data:
            # Verificar si ya existe un material planificado para este artículo y depósito
            material_existente = db.query(OTMaterial).filter(
                and_(
                    OTMaterial.ot_id == ot_id,
                    OTMaterial.codigo_art == material_data["codigo_art"],
                    OTMaterial.id_deposito == material_data["id_deposito"]
                )
            ).first()
            
            if material_existente:
                # Actualizar cantidad planificada
                material_existente.cantidad_planificada += material_data["cantidad_planificada"]
                material_existente.observacion = material_data.get("observacion", material_existente.observacion)
                materiales_creados.append(material_existente)
            else:
                # Crear nuevo material
                nuevo_material = OTMaterial(
                    ot_id=ot_id,
                    codigo_art=material_data["codigo_art"],
                    id_deposito=material_data["id_deposito"],
                    cantidad_planificada=material_data["cantidad_planificada"],
                    observacion=material_data.get("observacion"),
                    estado="planificado"
                )
                db.add(nuevo_material)
                materiales_creados.append(nuevo_material)
        
        db.commit()
        
        # Refresh todos los materiales
        for material in materiales_creados:
            db.refresh(material)
        
        logger.info(f"Planificados {len(materiales_creados)} materiales para OT {ot_id}")
        return materiales_creados
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al planificar materiales: {e}")
        raise

def consumir_material_ot(
    db: Session, 
    material_id: int, 
    cantidad_utilizada: float, 
    usuario_consumo: str,
    observacion: str = None
) -> Dict[str, Any]:
    """
    Registra el consumo de un material específico y genera el movimiento de stock
    """
    try:
        # Obtener el material
        material = get_ot_material(db, material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado")
        
        # Validaciones
        if material.estado == "cancelado":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El material está cancelado")
        
        cantidad_disponible = material.cantidad_planificada - material.cantidad_utilizada
        if cantidad_utilizada > cantidad_disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cantidad a consumir ({cantidad_utilizada}) excede la disponible ({cantidad_disponible})"
            )
        
        # Actualizar el material
        material.cantidad_utilizada += cantidad_utilizada
        material.usuario_consumo = usuario_consumo
        material.fecha_consumo = datetime.datetime.utcnow()
        if observacion:
            material.observacion = f"{material.observacion or ''}\nConsumo: {observacion}".strip()
        
        # Actualizar estado según consumo
        if material.cantidad_utilizada >= material.cantidad_planificada:
            material.estado = "consumido"
        elif material.cantidad_utilizada > 0:
            material.estado = "parcial"
        
        # Crear movimiento de stock (salida)
        nro_movimiento = generar_movimiento_stock_consumo(
            db, material, cantidad_utilizada, usuario_consumo, observacion
        )
        
        if nro_movimiento:
            material.nro_movimiento_stock = nro_movimiento
        
        db.commit()
        db.refresh(material)
        
        logger.info(f"Consumido {cantidad_utilizada} del material {material_id} para OT {material.ot_id}")
        
        return {
            "material_id": material_id,
            "cantidad_consumida": cantidad_utilizada,
            "cantidad_restante": material.cantidad_planificada - material.cantidad_utilizada,
            "estado": material.estado,
            "nro_movimiento_stock": nro_movimiento
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al consumir material: {e}")
        raise

def devolver_material_ot(
    db: Session,
    material_id: int,
    cantidad_devuelta: float,
    usuario_devolucion: str,
    observacion: str = None
) -> Dict[str, Any]:
    """
    Registra la devolución de material no utilizado al stock
    """
    try:
        # Obtener el material
        material = get_ot_material(db, material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado")
        
        # Validaciones
        cantidad_max_devolver = material.cantidad_planificada - material.cantidad_utilizada - material.cantidad_devuelta
        if cantidad_devuelta > cantidad_max_devolver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cantidad a devolver ({cantidad_devuelta}) excede la disponible ({cantidad_max_devolver})"
            )
        
        # Actualizar el material
        material.cantidad_devuelta += cantidad_devuelta
        material.fecha_devolucion = datetime.datetime.utcnow()
        if observacion:
            material.observacion = f"{material.observacion or ''}\nDevolución: {observacion}".strip()
        
        # Actualizar estado
        if (material.cantidad_utilizada + material.cantidad_devuelta) >= material.cantidad_planificada:
            material.estado = "devuelto" if material.cantidad_utilizada == 0 else "consumido"
        
        # Crear movimiento de stock (entrada - devolución)
        nro_movimiento = generar_movimiento_stock_devolucion(
            db, material, cantidad_devuelta, usuario_devolucion, observacion
        )
        
        db.commit()
        db.refresh(material)
        
        logger.info(f"Devuelto {cantidad_devuelta} del material {material_id} de OT {material.ot_id}")
        
        return {
            "material_id": material_id,
            "cantidad_devuelta": cantidad_devuelta,
            "estado": material.estado,
            "nro_movimiento_stock": nro_movimiento
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al devolver material: {e}")
        raise

def get_resumen_materiales_ot(db: Session, ot_id: int) -> Dict[str, Any]:
    """
    Obtiene un resumen completo de los materiales de una OT
    """
    try:
        materiales = get_materiales_by_ot(db, ot_id)
        
        if not materiales:
            return {
                "ot_id": ot_id,
                "total_materiales": 0,
                "materiales_planificados": [],
                "resumen": {
                    "total_planificado": 0,
                    "total_utilizado": 0,
                    "total_devuelto": 0,
                    "total_pendiente": 0,
                    "eficiencia_promedio": 0.0
                }
            }
        
        # Calcular totales
        total_planificado = sum(m.cantidad_planificada for m in materiales)
        total_utilizado = sum(m.cantidad_utilizada for m in materiales)
        total_devuelto = sum(m.cantidad_devuelta for m in materiales)
        total_pendiente = sum(m.cantidad_pendiente for m in materiales)
        
        # Calcular eficiencia promedio
        eficiencias = [m.porcentaje_utilizado for m in materiales if m.cantidad_planificada > 0]
        eficiencia_promedio = sum(eficiencias) / len(eficiencias) if eficiencias else 0.0
        
        # Preparar datos de materiales
        materiales_data = []
        for material in materiales:
            materiales_data.append({
                "id": material.id,
                "codigo_art": material.codigo_art,
                "id_deposito": material.id_deposito,
                "cantidad_planificada": material.cantidad_planificada,
                "cantidad_utilizada": material.cantidad_utilizada,
                "cantidad_devuelta": material.cantidad_devuelta,
                "cantidad_pendiente": material.cantidad_pendiente,
                "porcentaje_utilizado": material.porcentaje_utilizado,
                "estado": material.estado,
                "fecha_planificacion": material.fecha_planificacion,
                "fecha_consumo": material.fecha_consumo,
                "observacion": material.observacion
            })
        
        return {
            "ot_id": ot_id,
            "total_materiales": len(materiales),
            "materiales_planificados": materiales_data,
            "resumen": {
                "total_planificado": total_planificado,
                "total_utilizado": total_utilizado,
                "total_devuelto": total_devuelto,
                "total_pendiente": total_pendiente,
                "eficiencia_promedio": round(eficiencia_promedio, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error al obtener resumen de materiales: {e}")
        raise

# ===== Funciones auxiliares para Stock =====

def generar_movimiento_stock_consumo(
    db: Session,
    material: OTMaterial,
    cantidad: float,
    usuario: str,
    observacion: str = None
) -> Optional[int]:
    """
    Genera un movimiento de stock de salida por consumo de material en OT
    """
    try:
        # Obtener el último número de movimiento
        ultimo_mov = db.query(func.max(StockModel.nro_movimiento)).scalar() or 0
        nuevo_nro_movimiento = ultimo_mov + 1
        
        # Obtener stock actual del depósito
        stock_actual = db.query(StockModel).filter(
            and_(
                StockModel.id_deposito == material.id_deposito,
                StockModel.codigo_art == material.codigo_art
            )
        ).order_by(StockModel.id.desc()).first()
        
        if not stock_actual:
            logger.warning(f"No hay stock previo para artículo {material.codigo_art} en depósito {material.id_deposito}")
            return None
        
        # Calcular nuevas cantidades
        nueva_disponible = stock_actual.cant_disponible - cantidad
        
        # Crear registro de movimiento de stock
        movimiento_stock = StockModel(
            nro_movimiento=nuevo_nro_movimiento,
            codigo_art=material.codigo_art,
            id_deposito=material.id_deposito,
            cant_disponible=nueva_disponible,
            cant_reservado=stock_actual.cant_reservado,
            cant_preparado=stock_actual.cant_preparado,
            tipo=False,  # Salida
            fecha=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            observacion=f"Consumo OT #{material.ot_id} - {observacion or 'Material utilizado'} - Usuario: {usuario}"
        )
        
        db.add(movimiento_stock)
        db.flush()  # Para obtener el ID sin hacer commit
        
        logger.info(f"Movimiento de stock creado: {nuevo_nro_movimiento} (consumo OT)")
        return nuevo_nro_movimiento
        
    except Exception as e:
        logger.error(f"Error al generar movimiento de stock de consumo: {e}")
        return None

def generar_movimiento_stock_devolucion(
    db: Session,
    material: OTMaterial,
    cantidad: float,
    usuario: str,
    observacion: str = None
) -> Optional[int]:
    """
    Genera un movimiento de stock de entrada por devolución de material de OT
    """
    try:
        # Obtener el último número de movimiento
        ultimo_mov = db.query(func.max(StockModel.nro_movimiento)).scalar() or 0
        nuevo_nro_movimiento = ultimo_mov + 1
        
        # Obtener stock actual del depósito
        stock_actual = db.query(StockModel).filter(
            and_(
                StockModel.id_deposito == material.id_deposito,
                StockModel.codigo_art == material.codigo_art
            )
        ).order_by(StockModel.id.desc()).first()
        
        if not stock_actual:
            logger.warning(f"No hay stock previo para artículo {material.codigo_art} en depósito {material.id_deposito}")
            return None
        
        # Calcular nuevas cantidades
        nueva_disponible = stock_actual.cant_disponible + cantidad
        
        # Crear registro de movimiento de stock
        movimiento_stock = StockModel(
            nro_movimiento=nuevo_nro_movimiento,
            codigo_art=material.codigo_art,
            id_deposito=material.id_deposito,
            cant_disponible=nueva_disponible,
            cant_reservado=stock_actual.cant_reservado,
            cant_preparado=stock_actual.cant_preparado,
            tipo=True,  # Entrada
            fecha=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            observacion=f"Devolución OT #{material.ot_id} - {observacion or 'Material no utilizado'} - Usuario: {usuario}"
        )
        
        db.add(movimiento_stock)
        db.flush()  # Para obtener el ID sin hacer commit
        
        logger.info(f"Movimiento de stock creado: {nuevo_nro_movimiento} (devolución OT)")
        return nuevo_nro_movimiento
        
    except Exception as e:
        logger.error(f"Error al generar movimiento de stock de devolución: {e}")
        return None

def validar_disponibilidad_material(db: Session, codigo_art: int, id_deposito: int, cantidad_requerida: float) -> Dict[str, Any]:
    """
    Valida si hay suficiente stock disponible para un material
    """
    try:
        # Obtener stock actual
        stock_actual = db.query(StockModel).filter(
            and_(
                StockModel.id_deposito == id_deposito,
                StockModel.codigo_art == codigo_art
            )
        ).order_by(StockModel.id.desc()).first()
        
        if not stock_actual:
            return {
                "disponible": False,
                "stock_actual": 0.0,
                "cantidad_requerida": cantidad_requerida,
                "diferencia": cantidad_requerida,
                "mensaje": "No hay stock registrado para este artículo en el depósito"
            }
        
        disponible = stock_actual.cant_disponible >= cantidad_requerida
        diferencia = cantidad_requerida - stock_actual.cant_disponible
        
        return {
            "disponible": disponible,
            "stock_actual": stock_actual.cant_disponible,
            "cantidad_requerida": cantidad_requerida,
            "diferencia": max(0, diferencia),
            "mensaje": "Stock suficiente" if disponible else f"Faltan {diferencia} unidades"
        }
        
    except Exception as e:
        logger.error(f"Error al validar disponibilidad: {e}")
        return {
            "disponible": False,
            "stock_actual": 0.0,
            "cantidad_requerida": cantidad_requerida,
            "diferencia": cantidad_requerida,
            "mensaje": f"Error al validar: {str(e)}"
        }
