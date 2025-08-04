# Imports de bibliotecas estándar
from sql_app.Services.app_stock.articulos.model_facturacion import FacturaItem  # Importamos el modelo de items, Facturacion
from barcode.writer import ImageWriter
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from typing import Any, Dict, List, Optional, Tuple
import barcode
import base64
import json
import logging
import os
import re

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def create_facturacion(db: Session, facturacion: Dict[str, Any]) -> Facturacion:
    """
    Crea un nuevo registro de Facturacion en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Extraer los items si existen
        items = facturacion.pop('items', []) if isinstance(facturacion, dict) else []
        
        # Preparar los datos para la consulta principal
        facturacion_data = {}
        
        # Definir todos los campos de la tabla facturacion
        campos_factura = [
            'id', 'nrofactura', 'tipo_comprobante', 'fecha_emision', 'fecha_vencimiento',
            'emisor_razon_social', 'emisor_nombre_fantasia', 'emisor_cuit', 'emisor_domicilio',
            'emisor_localidad', 'emisor_provincia', 'emisor_codigo_postal', 'emisor_condicion_iva',
            'emisor_ingresos_brutos', 'emisor_inicio_actividades', 'receptor_tipo_documento',
            'receptor_nro_documento', 'receptor_razon_social', 'receptor_domicilio', 'receptor_localidad',
            'receptor_provincia', 'receptor_codigo_postal', 'receptor_condicion_iva', 'condicion_venta',
            'forma_pago', 'moneda', 'tipo_cambio', 'subtotal', 'descuento_porcentaje', 'descuento_importe',
            'subtotal_neto', 'iva_porcentaje', 'iva_importe', 'otros_impuestos', 'total', 'cae',
            'cae_vencimiento', 'estado', 'observaciones', 'anulada'
        ]
        
        # Llenar facturacion_data con los campos que vienen en el input
        for field in campos_factura:
            if field in facturacion:
                # Convertir fechas en formato string a objetos date
                if field in ['fecha_emision', 'fecha_vencimiento', 'emisor_inicio_actividades', 'cae_vencimiento'] and facturacion[field]:
                    if isinstance(facturacion[field], str):
                        try:
                            facturacion_data[field] = datetime.strptime(facturacion[field], "%Y-%m-%d").date()
                        except ValueError:
                            facturacion_data[field] = None
                    else:
                        facturacion_data[field] = facturacion[field]
                else:
                    facturacion_data[field] = facturacion[field]
        
        # Construir dinámicamente la consulta SQL INSERT
        campos = ", ".join(facturacion_data.keys())
        placeholders = ", ".join([f":{field}" for field in facturacion_data.keys()])
        
        # Construir cláusula OUTPUT para todos los campos
        output_fields = ", ".join([f"INSERTED.{field}" for field in campos_factura])
        
        query = text(f"""
            INSERT INTO facturacion ({campos})
            OUTPUT {output_fields}
            VALUES ({placeholders})
        """)
        
        # Ejecutar la consulta y obtener el registro insertado
        result = db.execute(query, facturacion_data)
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro de facturación no se pudo crear"
            )
        
        # Obtener el ID de la factura para los items
        factura_id = row[0]  # El ID es el primer campo
        
        # Crear un nuevo objeto Facturacion con los valores devueltos
        new_facturacion = Facturacion()
        
        # Asignar los valores devueltos al objeto
        for i, field in enumerate(campos_factura):
            if i < len(row):  # Protección contra índices fuera de rango
                setattr(new_facturacion, field, row[i])
        
        # Procesar los items de la factura si existen
        if items and isinstance(items, list):
            for item in items:
                item_data = {
                    'factura_id': factura_id,
                    'codigo': item.get('codigo'),
                    'descripcion': item.get('descripcion'),
                    'cantidad': item.get('cantidad', 1),
                    'unidad_medida': item.get('unidad_medida', 'unidad'),
                    'precio_unitario': item.get('precio_unitario', 0),
                    'bonificacion_porcentaje': item.get('bonificacion_porcentaje', 0),
                    'subtotal': item.get('subtotal', 0),
                    'alicuota_iva': item.get('alicuota_iva', 21),
                    'importe_iva': item.get('importe_iva', 0),
                    'importe_total': item.get('importe_total', 0),
                    'observaciones': item.get('observaciones')
                }
                
                # Construir la consulta para insertar el item
                item_campos = ", ".join(item_data.keys())
                item_placeholders = ", ".join([f":{field}" for field in item_data.keys()])
                
                item_query = text(f"""
                    INSERT INTO factura_items ({item_campos})
                    VALUES ({item_placeholders})
                """)
                
                # Ejecutar la consulta para el item
                db.execute(item_query, item_data)
        
        db.commit()
        return new_facturacion
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Facturacion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Facturacion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_facturacion(db: Session, id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un registro de Facturacion por su clave primaria usando SQL directo.
    Incluye sus items asociados.
    """
    try:
        # Consulta para obtener la factura
        factura_query = text("""
            SELECT 
                id, nrofactura, tipo_comprobante, fecha_emision, fecha_vencimiento,
                emisor_razon_social, emisor_nombre_fantasia, emisor_cuit, emisor_domicilio,
                emisor_localidad, emisor_provincia, emisor_codigo_postal, emisor_condicion_iva,
                emisor_ingresos_brutos, emisor_inicio_actividades, receptor_tipo_documento,
                receptor_nro_documento, receptor_razon_social, receptor_domicilio, receptor_localidad,
                receptor_provincia, receptor_codigo_postal, receptor_condicion_iva, condicion_venta,
                forma_pago, moneda, tipo_cambio, subtotal, descuento_porcentaje, descuento_importe,
                subtotal_neto, iva_porcentaje, iva_importe, otros_impuestos, total, cae,
                cae_vencimiento, estado, observaciones, creado_en, actualizado_en, anulada
            FROM facturacion 
            WHERE id = :id
        """)
        factura_result = db.execute(factura_query, {"id": id}).first()
        
        if not factura_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada.")
        
        # Definir nombres de columnas para la factura
        factura_columns = [
            'id', 'nrofactura', 'tipo_comprobante', 'fecha_emision', 'fecha_vencimiento',
            'emisor_razon_social', 'emisor_nombre_fantasia', 'emisor_cuit', 'emisor_domicilio',
            'emisor_localidad', 'emisor_provincia', 'emisor_codigo_postal', 'emisor_condicion_iva',
            'emisor_ingresos_brutos', 'emisor_inicio_actividades', 'receptor_tipo_documento',
            'receptor_nro_documento', 'receptor_razon_social', 'receptor_domicilio', 'receptor_localidad',
            'receptor_provincia', 'receptor_codigo_postal', 'receptor_condicion_iva', 'condicion_venta',
            'forma_pago', 'moneda', 'tipo_cambio', 'subtotal', 'descuento_porcentaje', 'descuento_importe',
            'subtotal_neto', 'iva_porcentaje', 'iva_importe', 'otros_impuestos', 'total', 'cae',
            'cae_vencimiento', 'estado', 'observaciones', 'creado_en', 'actualizado_en', 'anulada'
        ]
        
        # Crear un diccionario para la factura
        factura_dict = dict(zip(factura_columns, factura_result))
        
        # Convertir fechas a formato string para serialización JSON
        for field in ['fecha_emision', 'fecha_vencimiento', 'emisor_inicio_actividades', 'cae_vencimiento', 'creado_en', 'actualizado_en']:
            if factura_dict[field] is not None:
                if isinstance(factura_dict[field], (datetime.date, datetime.datetime)):
                    factura_dict[field] = factura_dict[field].isoformat()
        
        # Consulta para obtener los items de la factura
        items_query = text("""
            SELECT 
                id, factura_id, codigo, descripcion, cantidad, unidad_medida, 
                precio_unitario, bonificacion_porcentaje, subtotal, alicuota_iva, 
                importe_iva, importe_total, observaciones
            FROM factura_items 
            WHERE factura_id = :factura_id
        """)
        items_result = db.execute(items_query, {"factura_id": id}).fetchall()
        
        # Definir nombres de columnas para los items
        item_columns = [
            'id', 'factura_id', 'codigo', 'descripcion', 'cantidad', 'unidad_medida', 
            'precio_unitario', 'bonificacion_porcentaje', 'subtotal', 'alicuota_iva', 
            'importe_iva', 'importe_total', 'observaciones'
        ]
        
        # Crear lista de items
        items = []
        for item_row in items_result:
            item_dict = dict(zip(item_columns, item_row))
            items.append(item_dict)
        
        # Agregar items a la factura
        factura_dict['items'] = items
        
        return factura_dict
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_facturacion(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Obtiene una lista de todos los registros de Facturacion usando SQL directo.
    """
    try:
        # Consulta para obtener las facturas con paginación
        facturas_query = text("""
            SELECT 
                id, nrofactura, tipo_comprobante, fecha_emision, receptor_razon_social,
                total, estado, anulada
            FROM facturacion
            ORDER BY fecha_emision DESC
            OFFSET :skip ROWS
            FETCH NEXT :limit ROWS ONLY
        """)
        
        facturas_result = db.execute(facturas_query, {"skip": skip, "limit": limit}).fetchall()
        
        # Definir nombres de columnas para las facturas (versión resumida)
        factura_columns = [
            'id', 'nrofactura', 'tipo_comprobante', 'fecha_emision', 'receptor_razon_social',
            'total', 'estado', 'anulada'
        ]
        
        # Crear lista de facturas
        facturas = []
        for factura_row in facturas_result:
            factura_dict = dict(zip(factura_columns, factura_row))
            
            # Convertir fechas a formato string para serialización JSON
            if 'fecha_emision' in factura_dict and factura_dict['fecha_emision'] is not None:
                if isinstance(factura_dict['fecha_emision'], (datetime.date, datetime.datetime)):
                    factura_dict['fecha_emision'] = factura_dict['fecha_emision'].isoformat()
            
            facturas.append(factura_dict)
        
        return facturas
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_facturacion(db: Session, id: int) -> Dict[str, Any]:
    """
    Elimina un registro de Facturacion por su clave primaria usando SQL directo.
    También elimina sus items asociados.
    """
    try:
        # Primero obtener los datos de la factura para devolverlos luego
        factura = get_facturacion(db, id)
        if not factura:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada.")
        
        # Eliminar los items de la factura primero
        delete_items_query = text("""
            DELETE FROM factura_items
            WHERE factura_id = :factura_id
        """)
        db.execute(delete_items_query, {"factura_id": id})
        
        # Luego eliminar la factura
        delete_factura_query = text("""
            DELETE FROM facturacion 
            WHERE id = :id
        """)
        db.execute(delete_factura_query, {"id": id})
        
        db.commit()
        return factura
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_facturacion(db: Session, id: int, facturacion_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza un registro de Facturacion por su clave primaria usando SQL directo.
    También actualiza sus items asociados.
    """
    logger.info(f"Actualizando Facturacion con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM facturacion WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada.")
        
        # Extraer los items si existen
        items = facturacion_data.pop('items', []) if isinstance(facturacion_data, dict) else []
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        facturacion_data_copy = facturacion_data.copy()
        if 'id' in facturacion_data_copy:
            del facturacion_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not facturacion_data_copy:
            return get_facturacion(db, id)
        
        # Convertir fechas en formato string a objetos date
        for field in ['fecha_emision', 'fecha_vencimiento', 'emisor_inicio_actividades', 'cae_vencimiento']:
            if field in facturacion_data_copy and facturacion_data_copy[field]:
                if isinstance(facturacion_data_copy[field], str):
                    try:
                        facturacion_data_copy[field] = datetime.strptime(facturacion_data_copy[field], "%Y-%m-%d").date()
                    except ValueError:
                        facturacion_data_copy[field] = None
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in facturacion_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa
        query = text(f"""
            UPDATE facturacion
            SET {set_clause_str}
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = facturacion_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        db.execute(query, params)
        
        # Procesar los items si existen
        if items and isinstance(items, list):
            # Primero, eliminar los items existentes
            delete_items_query = text("""
                DELETE FROM factura_items
                WHERE factura_id = :factura_id
            """)
            db.execute(delete_items_query, {"factura_id": id})
            
            # Luego, insertar los nuevos items
            for item in items:
                item_data = {
                    'factura_id': id,
                    'codigo': item.get('codigo'),
                    'descripcion': item.get('descripcion'),
                    'cantidad': item.get('cantidad', 1),
                    'unidad_medida': item.get('unidad_medida', 'unidad'),
                    'precio_unitario': item.get('precio_unitario', 0),
                    'bonificacion_porcentaje': item.get('bonificacion_porcentaje', 0),
                    'subtotal': item.get('subtotal', 0),
                    'alicuota_iva': item.get('alicuota_iva', 21),
                    'importe_iva': item.get('importe_iva', 0),
                    'importe_total': item.get('importe_total', 0),
                    'observaciones': item.get('observaciones')
                }
                
                # Construir la consulta para insertar el item
                item_campos = ", ".join(item_data.keys())
                item_placeholders = ", ".join([f":{field}" for field in item_data.keys()])
                
                item_query = text(f"""
                    INSERT INTO factura_items ({item_campos})
                    VALUES ({item_placeholders})
                """)
                
                # Ejecutar la consulta para el item
                db.execute(item_query, item_data)
        
        db.commit()
        
        # Obtener la factura actualizada con sus items
        return get_facturacion(db, id)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")

def busqueda_avanzada_facturacion(db: Session, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Realiza una búsqueda avanzada de facturas según múltiples criterios.
    """
    try:
        # Inicializar la consulta base
        query_str = """
            SELECT 
                id, nrofactura, tipo_comprobante, fecha_emision, receptor_razon_social, 
                total, estado, anulada
            FROM facturacion
            WHERE 1=1
        """
        
        # Diccionario para los parámetros de la consulta
        params = {}
        
        # Agregar condiciones según los filtros recibidos
        if 'nrofactura' in filtros and filtros['nrofactura']:
            query_str += " AND nrofactura LIKE :nrofactura"
            params['nrofactura'] = f"%{filtros['nrofactura']}%"
        
        if 'tipo_comprobante' in filtros and filtros['tipo_comprobante']:
            query_str += " AND tipo_comprobante = :tipo_comprobante"
            params['tipo_comprobante'] = filtros['tipo_comprobante']
        
        if 'fecha_desde' in filtros and filtros['fecha_desde']:
            query_str += " AND fecha_emision >= :fecha_desde"
            fecha_desde = filtros['fecha_desde']
            if isinstance(fecha_desde, str):
                fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            params['fecha_desde'] = fecha_desde
        
        if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
            query_str += " AND fecha_emision <= :fecha_hasta"
            fecha_hasta = filtros['fecha_hasta']
            if isinstance(fecha_hasta, str):
                fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
            params['fecha_hasta'] = fecha_hasta
        
        if 'receptor_razon_social' in filtros and filtros['receptor_razon_social']:
            query_str += " AND receptor_razon_social LIKE :receptor_razon_social"
            params['receptor_razon_social'] = f"%{filtros['receptor_razon_social']}%"
        
        if 'receptor_nro_documento' in filtros and filtros['receptor_nro_documento']:
            query_str += " AND receptor_nro_documento LIKE :receptor_nro_documento"
            params['receptor_nro_documento'] = f"%{filtros['receptor_nro_documento']}%"
        
        if 'estado' in filtros and filtros['estado']:
            query_str += " AND estado = :estado"
            params['estado'] = filtros['estado']
        
        if 'monto_min' in filtros and filtros['monto_min'] is not None:
            query_str += " AND total >= :monto_min"
            params['monto_min'] = filtros['monto_min']
        
        if 'monto_max' in filtros and filtros['monto_max'] is not None:
            query_str += " AND total <= :monto_max"
            params['monto_max'] = filtros['monto_max']
        
        # Agregar ordenamiento
        order_by = filtros.get('order_by', 'fecha_emision')
        order_dir = filtros.get('order_dir', 'DESC')
        query_str += f" ORDER BY {order_by} {order_dir}"
        
        # Agregar paginación
        limit = filtros.get('limit', 100)
        skip = filtros.get('skip', 0)
        query_str += " OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY"
        params['skip'] = skip
        params['limit'] = limit
        
        # Ejecutar la consulta
        result = db.execute(text(query_str), params).fetchall()
        
        # Definir nombres de columnas para las facturas
        factura_columns = [
            'id', 'nrofactura', 'tipo_comprobante', 'fecha_emision', 'receptor_razon_social',
            'total', 'estado', 'anulada'
        ]
        
        # Crear lista de facturas
        facturas = []
        for row in result:
            factura_dict = dict(zip(factura_columns, row))
            
            # Convertir fechas a formato string
            if factura_dict['fecha_emision'] is not None:
                if isinstance(factura_dict['fecha_emision'], (datetime.date, datetime.datetime)):
                    factura_dict['fecha_emision'] = factura_dict['fecha_emision'].isoformat()
            
            facturas.append(factura_dict)
        
        return facturas
    except SQLAlchemyError as e:
        logger.error(f"Error en la búsqueda avanzada de Facturacion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la búsqueda: {str(e)}")

def generar_pdf_factura(db: Session, id: int) -> Tuple[BytesIO, str]:
    """
    Genera un archivo PDF para una factura específica.
    Devuelve un BytesIO con el contenido PDF y el nombre de archivo sugerido.
    """
    try:
        # Obtener los datos de la factura
        factura = get_facturacion(db, id)
        if not factura:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada.")
        
        # Crear un buffer para el PDF
        buffer = BytesIO()
        
        # Crear el PDF con ReportLab
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Configurar título y metadatos
        c.setTitle(f"Factura {factura['tipo_comprobante']} N° {factura['nrofactura']}")
        c.setAuthor(factura['emisor_razon_social'])
        c.setSubject(f"Factura para {factura['receptor_razon_social']}")
        
        # Dibujar encabezado
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, height - 50, f"FACTURA {factura['tipo_comprobante']}")
        
        # Recuadro para el tipo de factura
        c.rect(width - 60, height - 55, 30, 30)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width - 45, height - 40, factura['tipo_comprobante'])
        
        # Dibujar información de la empresa emisora
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 80, factura['emisor_razon_social'])
        c.setFont("Helvetica", 9)
        c.drawString(30, height - 95, f"CUIT: {factura['emisor_cuit']}")
        c.drawString(30, height - 110, f"Domicilio: {factura['emisor_domicilio']}")
        c.drawString(30, height - 125, f"{factura['emisor_localidad']}, {factura['emisor_provincia']} ({factura['emisor_codigo_postal']})")
        c.drawString(30, height - 140, f"Condición frente al IVA: {factura['emisor_condicion_iva']}")
        
        if factura.get('emisor_ingresos_brutos'):
            c.drawString(30, height - 155, f"Ingresos Brutos: {factura['emisor_ingresos_brutos']}")
        
        if factura.get('emisor_inicio_actividades'):
            c.drawString(30, height - 170, f"Fecha de inicio de actividades: {factura['emisor_inicio_actividades']}")
        
        # Información de la factura
        c.setFont("Helvetica", 10)
        c.drawString(width - 200, height - 95, f"Número: {factura['nrofactura']}")
        c.drawString(width - 200, height - 110, f"Fecha de emisión: {factura['fecha_emision']}")
        
        if factura.get('fecha_vencimiento'):
            c.drawString(width - 200, height - 125, f"Fecha de vencimiento: {factura['fecha_vencimiento']}")
        
        # Línea separadora
        c.line(30, height - 190, width - 30, height - 190)
        
        # Datos del receptor
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30, height - 210, "Datos del cliente:")
        c.setFont("Helvetica", 10)
        c.drawString(30, height - 230, f"Razón Social: {factura['receptor_razon_social']}")
        c.drawString(30, height - 245, f"{factura['receptor_tipo_documento']}: {factura['receptor_nro_documento']}")
        c.drawString(30, height - 260, f"Condición frente al IVA: {factura['receptor_condicion_iva']}")
        
        if factura.get('receptor_domicilio'):
            c.drawString(30, height - 275, f"Domicilio: {factura['receptor_domicilio']}")
            
            if factura.get('receptor_localidad') and factura.get('receptor_provincia'):
                c.drawString(30, height - 290, f"{factura.get('receptor_localidad', '')}, {factura.get('receptor_provincia', '')}")
                if factura.get('receptor_codigo_postal'):
                    c.drawString(30, height - 305, f"CP: {factura['receptor_codigo_postal']}")
        
        # Información de la operación
        c.drawString(width - 200, height - 230, f"Condición de venta: {factura['condicion_venta']}")
        if factura.get('forma_pago'):
            c.drawString(width - 200, height - 245, f"Forma de pago: {factura['forma_pago']}")
        
        # Línea separadora
        c.line(30, height - 325, width - 30, height - 325)
        
        # Tabla de productos
        items = factura.get('items', [])
        if items:
            data = [['Código', 'Descripción', 'Cant.', 'U. Medida', 'Precio Unit.', 'Bonif.', 'Subtotal', 'IVA %', 'Total']]
            
            for item in items:
                data.append([
                    item.get('codigo', ''),
                    item.get('descripcion', ''),
                    str(item.get('cantidad', '')),
                    item.get('unidad_medida', ''),
                    f"${item.get('precio_unitario', 0):.2f}",
                    f"{item.get('bonificacion_porcentaje', 0):.2f}%" if item.get('bonificacion_porcentaje') else "",
                    f"${item.get('subtotal', 0):.2f}",
                    f"{item.get('alicuota_iva', 0):.2f}%",
                    f"${item.get('importe_total', 0):.2f}"
                ])
            
            table = Table(data, colWidths=[40, 180, 30, 40, 60, 40, 60, 40, 60])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Alinear descripción a la izquierda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            
            # Posicionar la tabla
            table.wrapOn(c, width - 60, height)
            table.drawOn(c, 30, height - 340 - (len(items) * 20))
        
        # Calcular la posición Y final después de la tabla
        final_y = height - 340 - (len(items) * 20) - 30 if items else height - 340
        
        # Resumen de importes
        c.setFont("Helvetica-Bold", 10)
        c.drawString(width - 200, final_y - 20, "Resumen de importes:")
        c.setFont("Helvetica", 10)
        
        c.drawString(width - 200, final_y - 35, f"Subtotal: ${factura.get('subtotal', 0):.2f}")
        
        if factura.get('descuento_importe', 0) > 0:
            c.drawString(width - 200, final_y - 50, f"Descuento ({factura.get('descuento_porcentaje', 0):.2f}%): -${factura.get('descuento_importe', 0):.2f}")
            c.drawString(width - 200, final_y - 65, f"Subtotal neto: ${factura.get('subtotal_neto', 0):.2f}")
            y_offset = 80
        else:
            y_offset = 50
        
        c.drawString(width - 200, final_y - y_offset, f"IVA ({factura.get('iva_porcentaje', 0):.2f}%): ${factura.get('iva_importe', 0):.2f}")
        
        if factura.get('otros_impuestos', 0) > 0:
            c.drawString(width - 200, final_y - (y_offset + 15), f"Otros impuestos: ${factura.get('otros_impuestos', 0):.2f}")
            y_offset += 15
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(width - 200, final_y - (y_offset + 20), f"TOTAL: ${factura.get('total', 0):.2f}")
        
        # Información de CAE si existe
        if factura.get('cae'):
            c.setFont("Helvetica", 9)
            c.drawString(30, 60, f"CAE N°: {factura['cae']}")
            c.drawString(30, 45, f"Fecha de vto. de CAE: {factura['cae_vencimiento']}")
            
            # Generar código de barras para el CAE
            cae_text = f"{factura['emisor_cuit'].replace('-', '')}{factura['tipo_comprobante']}{factura['nrofactura']}{factura['cae']}{factura['cae_vencimiento'].replace('-', '')}"
            
            try:
                # Intentar generar el código de barras
                barcode_io = BytesIO()
                code = barcode.get('code128', cae_text, writer=ImageWriter())
                code.write(barcode_io)
                barcode_io.seek(0)
                
                # Importar la imagen del código de barras
                from reportlab.lib.utils import ImageReader
                img = ImageReader(barcode_io)
                
                # Dibujar el código de barras
                c.drawImage(img, 30, 70, width=300, height=40)
            except:
                # Si falla la generación del código de barras, simplemente omitirlo
                logger.warning("No se pudo generar el código de barras para el CAE")
        
        # Pie de página
        c.setFont("Helvetica", 8)
        c.drawString(30, 30, "Este documento es una factura electrónica válida según normativa AFIP.")
        
        # Finalizar el documento
        c.save()
        buffer.seek(0)
        
        # Nombre de archivo sugerido
        filename = f"Factura_{factura['tipo_comprobante']}_{factura['nrofactura']}.pdf"
        
        return buffer, filename
    except Exception as e:
        logger.error(f"Error al generar PDF de factura: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al generar el PDF: {str(e)}")
        
def enviar_factura_por_email(db: Session, id: int, email_destino: str, asunto: str = None, cuerpo: str = None) -> Dict[str, Any]:
    """
    Envía una factura por email al destinatario especificado.
    Requiere tener configurado un servicio de correo electrónico.
    """
    try:
        from ..mail.mail import enviar_email_con_adjunto
        
        # Obtener datos de la factura y generar PDF
        factura = get_facturacion(db, id)
        if not factura:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada.")
        
        # Generar PDF
        pdf_buffer, filename = generar_pdf_factura(db, id)
        
        # Asunto por defecto
        if not asunto:
            asunto = f"Factura {factura['tipo_comprobante']} N° {factura['nrofactura']}"
        
        # Cuerpo del email por defecto
        if not cuerpo:
            cuerpo = f"""
            <html>
            <body>
                <p>Estimado/a cliente {factura['receptor_razon_social']},</p>
                <p>Adjunto enviamos su factura {factura['tipo_comprobante']} N° {factura['nrofactura']} 
                por un total de ${factura['total']:.2f}.</p>
                <p>Fecha de emisión: {factura['fecha_emision']}</p>
                <p>Por favor, no responda a este correo ya que es generado automáticamente.</p>
                <p>Saludos cordiales,<br>{factura['emisor_razon_social']}</p>
            </body>
            </html>
            """
        
        # Preparar el archivo adjunto
        pdf_content = pdf_buffer.getvalue()
        
        # Enviar el email con el adjunto
        resultado = enviar_email_con_adjunto(
            destinatario=email_destino,
            asunto=asunto,
            contenido=cuerpo,
            nombre_adjunto=filename,
            contenido_adjunto=pdf_content,
            tipo_contenido="application/pdf"
        )
        
        return {"mensaje": "Factura enviada correctamente por email", "destinatario": email_destino, "resultado": resultado}
    except ImportError:
        logger.error("Módulo de correo no disponible")
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Servicio de correo no disponible")
    except Exception as e:
        logger.error(f"Error al enviar factura por email: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al enviar el email: {str(e)}")

def obtener_numero_factura(db: Session, tipo_comprobante: str) -> str:
    """
    Obtiene el próximo número de factura para un tipo de comprobante.
    """
    try:
        # Obtener el último número para este tipo de comprobante
        result = db.execute(
            text("""
                SELECT MAX(CAST(nrofactura AS INT)) 
                FROM facturacion 
                WHERE tipo_comprobante = :tipo_comprobante
            """),
            {"tipo_comprobante": tipo_comprobante}
        ).scalar()
        
        # Si no hay facturas previas, comenzar desde 1
        if result is None:
            proximo_numero = 1
        else:
            proximo_numero = int(result) + 1
        
        # Formatear con ceros a la izquierda (8 dígitos)
        return f"{proximo_numero:08d}"
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener número de factura: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener número de factura: {str(e)}")

def anular_factura(db: Session, id: int, motivo: str = None) -> Dict[str, Any]:
    """
    Anula una factura (marcándola como anulada).
    """
    try:
        # Verificar que la factura existe
        factura = get_facturacion(db, id)
        if not factura:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada.")
        
        # Actualizar la factura para marcarla como anulada
        query = text("""
            UPDATE facturacion
            SET anulada = 1, 
                estado = 'Anulada',
                observaciones = CASE 
                    WHEN observaciones IS NULL THEN :motivo 
                    ELSE observaciones + CHAR(13) + CHAR(10) + 'Anulada: ' + :motivo 
                END
            WHERE id = :id
        """)
        
        db.execute(query, {"id": id, "motivo": f"Anulada: {motivo}" if motivo else "Anulada"})
        db.commit()
        
        # Obtener la factura actualizada
        factura_actualizada = get_facturacion(db, id)
        
        return factura_actualizada
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al anular factura: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al anular la factura: {str(e)}")

def calcular_totales(db: Session, items: List[Dict[str, Any]], descuento_porcentaje: float = 0) -> Dict[str, float]:
    """
    Calcula los totales de una factura a partir de los items.
    """
    try:
        subtotal = 0
        iva_importe = 0
        
        for item in items:
            cantidad = float(item.get('cantidad', 1))
            precio_unitario = float(item.get('precio_unitario', 0))
            bonificacion = float(item.get('bonificacion_porcentaje', 0)) / 100
            alicuota_iva = float(item.get('alicuota_iva', 21)) / 100
            
            # Calcular subtotal del ítem con bonificación
            precio_con_bonificacion = precio_unitario * (1 - bonificacion)
            subtotal_item = cantidad * precio_con_bonificacion
            
            # Calcular IVA del ítem
            iva_item = subtotal_item * alicuota_iva
            
            # Acumular totales
            subtotal += subtotal_item
            iva_importe += iva_item
            
            # Actualizar los valores calculados en el ítem
            item['subtotal'] = subtotal_item
            item['importe_iva'] = iva_item
            item['importe_total'] = subtotal_item + iva_item
        
        # Aplicar descuento general si existe
        descuento_importe = subtotal * (descuento_porcentaje / 100) if descuento_porcentaje else 0
        subtotal_neto = subtotal - descuento_importe
        
        # Recalcular IVA después de descuento si aplica a toda la factura
        if descuento_porcentaje:
            iva_importe = 0
            for item in items:
                # Ajustar el IVA proporcionalmente al descuento
                item['subtotal'] = item['subtotal'] * (1 - descuento_porcentaje / 100)
                item['importe_iva'] = item['subtotal'] * (float(item.get('alicuota_iva', 21)) / 100)
                item['importe_total'] = item['subtotal'] + item['importe_iva']
                iva_importe += item['importe_iva']
        
        # Calcular total final
        total = subtotal_neto + iva_importe
        
        return {
            'subtotal': subtotal,
            'descuento_porcentaje': descuento_porcentaje,
            'descuento_importe': descuento_importe,
            'subtotal_neto': subtotal_neto,
            'iva_importe': iva_importe,
            'total': total,
            'items': items
        }
    except Exception as e:
        logger.error(f"Error al calcular totales: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en el cálculo de totales: {str(e)}")

def obtener_estadisticas(db: Session, filtros: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre las facturas.
    """
    try:
        # Inicializar filtros si no existen
        if filtros is None:
            filtros = {}
        
        # Construir la consulta base con condiciones
        query_base = """
            FROM facturacion
            WHERE anulada = 0
        """
        
        # Diccionario para los parámetros de la consulta
        params = {}
        
        # Agregar condiciones según los filtros recibidos
        if 'fecha_desde' in filtros and filtros['fecha_desde']:
            query_base += " AND fecha_emision >= :fecha_desde"
            fecha_desde = filtros['fecha_desde']
            if isinstance(fecha_desde, str):
                fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            params['fecha_desde'] = fecha_desde
        
        if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
            query_base += " AND fecha_emision <= :fecha_hasta"
            fecha_hasta = filtros['fecha_hasta']
            if isinstance(fecha_hasta, str):
                fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
            params['fecha_hasta'] = fecha_hasta
        
        # Total de facturas
        total_facturas = db.execute(
            text(f"SELECT COUNT(*) {query_base}"), 
            params
        ).scalar()
        
        # Total facturado
        total_facturado = db.execute(
            text(f"SELECT SUM(total) {query_base}"), 
            params
        ).scalar() or 0
        
        # Facturas por tipo de comprobante
        facturas_por_tipo = db.execute(
            text(f"SELECT tipo_comprobante, COUNT(*) as cantidad, SUM(total) as total {query_base} GROUP BY tipo_comprobante"), 
            params
        ).fetchall()
        
        # Facturas por estado
        facturas_por_estado = db.execute(
            text(f"SELECT estado, COUNT(*) as cantidad {query_base} GROUP BY estado"), 
            params
        ).fetchall()
        
        # Facturas por mes (últimos 12 meses)
        facturas_por_mes = db.execute(
            text(f"""
                SELECT 
                    YEAR(fecha_emision) as año, 
                    MONTH(fecha_emision) as mes, 
                    COUNT(*) as cantidad, 
                    SUM(total) as total 
                {query_base} 
                GROUP BY YEAR(fecha_emision), MONTH(fecha_emision)
                ORDER BY YEAR(fecha_emision), MONTH(fecha_emision)
            """), 
            params
        ).fetchall()
        
        # Clientes con mayor facturación
        top_clientes = db.execute(
            text(f"""
                SELECT 
                    receptor_razon_social, 
                    receptor_nro_documento,
                    COUNT(*) as cantidad_facturas, 
                    SUM(total) as total_facturado 
                {query_base} 
                GROUP BY receptor_razon_social, receptor_nro_documento
                ORDER BY total_facturado DESC
                LIMIT 10
            """), 
            params
        ).fetchall()
        
        # Estructurar los resultados
        resultados = {
            "total_facturas": total_facturas,
            "total_facturado": total_facturado,
            "facturas_por_tipo": [{"tipo": row[0], "cantidad": row[1], "total": row[2]} for row in facturas_por_tipo],
            "facturas_por_estado": [{"estado": row[0], "cantidad": row[1]} for row in facturas_por_estado],
            "facturas_por_mes": [{"año": row[0], "mes": row[1], "cantidad": row[2], "total": row[3]} for row in facturas_por_mes],
            "top_clientes": [{"razon_social": row[0], "documento": row[1], "cantidad_facturas": row[2], "total_facturado": row[3]} for row in top_clientes]
        }
        
        return resultados
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener estadísticas: {str(e)}")
