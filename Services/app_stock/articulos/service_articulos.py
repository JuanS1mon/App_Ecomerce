from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text, or_
from .model_articulos import Articulos
from .model_precios_historial import PreciosHistorial  # Importando el modelo de precios historial
from .service_precios_historial import registrar_cambio_precio
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import barcode
from barcode.writer import ImageWriter
import qrcode
from io import BytesIO
import base64
import os
import uuid

logger = logging.getLogger(__name__)

def create_articulos(db: Session, articulos: Articulos) -> Articulos:
    """
    Crea un nuevo registro de Articulos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Preparar los datos para la consulta
        articulos_data = {}
        
        for field in ['codigo', 'descripcion', 'preciocosto', 'precioventa', 'modelo', 'marca', 'id_tipo']:
            if hasattr(articulos, field):
                articulos_data[field] = getattr(articulos, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO articulos (codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo)
            OUTPUT INSERTED.id, INSERTED.codigo, INSERTED.descripcion, INSERTED.preciocosto, INSERTED.precioventa, INSERTED.modelo, INSERTED.marca, INSERTED.id_tipo
            VALUES (:codigo, :descripcion, :preciocosto, :precioventa, :modelo, :marca, :id_tipo)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, articulos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Articulos con los valores devueltos
        new_articulos = Articulos()
        new_articulos.id = row[0]
        new_articulos.codigo = row[1]
        new_articulos.descripcion = row[2]
        new_articulos.preciocosto = row[3]
        new_articulos.precioventa = row[4]
        new_articulos.modelo = row[5]
        new_articulos.marca = row[6]
        new_articulos.id_tipo = row[7]
        
        return new_articulos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Articulos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Articulos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_articulos(db: Session, id: int) -> Optional[Articulos]:
    """
    Obtiene un registro de Articulos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo FROM articulos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Crear el objeto directamente con los valores
        articulos = Articulos()
        articulos.id = result[0]
        articulos.codigo = result[1]
        articulos.descripcion = result[2]
        articulos.preciocosto = result[3]
        articulos.precioventa = result[4]
        articulos.modelo = result[5]
        articulos.marca = result[6]
        articulos.id_tipo = result[7]
        
        return articulos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_articulos(db: Session) -> List[Articulos]:
    """
    Obtiene una lista de todos los registros de Articulos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo FROM articulos")
        )
        
        articuloss = []
        for row in result.fetchall():
            articulos = Articulos()
            articulos.id = row[0]
            articulos.codigo = row[1]
            articulos.descripcion = row[2]
            articulos.preciocosto = row[3]
            articulos.precioventa = row[4]
            articulos.modelo = row[5]
            articulos.marca = row[6]
            articulos.id_tipo = row[7]
            articuloss.append(articulos)
        
        return articuloss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_articulos(db: Session, id: int) -> Articulos:
    """
    Elimina un registro de Articulos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM articulos 
                OUTPUT DELETED.id, DELETED.codigo, DELETED.descripcion, DELETED.preciocosto, DELETED.precioventa, DELETED.modelo, DELETED.marca, DELETED.id_tipo
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_articulos = Articulos()
        deleted_articulos.id = result[0]
        deleted_articulos.codigo = result[1]
        deleted_articulos.descripcion = result[2]
        deleted_articulos.preciocosto = result[3]
        deleted_articulos.precioventa = result[4]
        deleted_articulos.modelo = result[5]
        deleted_articulos.marca = result[6]
        deleted_articulos.id_tipo = result[7]
        
        db.commit()
        return deleted_articulos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_articulos(db: Session, id: int, articulos_data: Dict[str, Any], usuario_id: Optional[int] = None, motivo: Optional[str] = None) -> Articulos:
    """
    Actualiza un registro de Articulos por su clave primaria usando SQL directo.
    Registra cambios de precio en el historial si los hay.
    """
    logger.info(f"Actualizando Articulos con id = {id}")
    try:
        # Obtener el artículo actual para registrar cambios de precio
        articulo_actual = None
        if 'preciocosto' in articulos_data or 'precioventa' in articulos_data:
            articulo_actual = get_articulos(db, id)
            if not articulo_actual:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Verificar que el registro existe si no se obtuvo previamente
        if not articulo_actual:
            result = db.execute(
                text("SELECT COUNT(*) FROM articulos WHERE id = :id"),
                {"id": id}
            ).scalar()
            
            if result == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        articulos_data_copy = articulos_data.copy()
        if 'id' in articulos_data_copy:
            del articulos_data_copy['id']
        
        # Eliminar campos que no existen en la tabla de artículos
        campos_no_validos = ['codigo_barras', 'codigo_barras_tipo', 'qr_data', 'imagen_codigo_url']
        for campo in campos_no_validos:
            if campo in articulos_data_copy:
                del articulos_data_copy[campo]
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not articulos_data_copy:
            return get_articulos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in articulos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE articulos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.codigo, INSERTED.descripcion, INSERTED.preciocosto, INSERTED.precioventa, INSERTED.modelo, INSERTED.marca, INSERTED.id_tipo
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = articulos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Articulos.")
        
        # Crear el objeto con los datos actualizados
        updated_articulos = Articulos()
        updated_articulos.id = result[0]
        updated_articulos.codigo = result[1]
        updated_articulos.descripcion = result[2]
        updated_articulos.preciocosto = result[3]
        updated_articulos.precioventa = result[4]
        updated_articulos.modelo = result[5]
        updated_articulos.marca = result[6]
        updated_articulos.id_tipo = result[7]
        
        # Registrar cambios de precio en el historial
        if articulo_actual:
            # Si se actualizó el precio de costo
            if 'preciocosto' in articulos_data_copy and articulo_actual.preciocosto != updated_articulos.preciocosto:
                registrar_cambio_precio(
                    db=db,
                    articulo_id=id,
                    precio_anterior=articulo_actual.preciocosto,
                    precio_nuevo=updated_articulos.preciocosto,
                    tipo_precio='costo',
                    usuario_id=usuario_id,
                    motivo=motivo
                )
                
            # Si se actualizó el precio de venta
            if 'precioventa' in articulos_data_copy and articulo_actual.precioventa != updated_articulos.precioventa:
                registrar_cambio_precio(
                    db=db, 
                    articulo_id=id,
                    precio_anterior=articulo_actual.precioventa,
                    precio_nuevo=updated_articulos.precioventa,
                    tipo_precio='venta',
                    usuario_id=usuario_id,
                    motivo=motivo
                )
        
        return updated_articulos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")


def actualizar_precio_articulo(
    db: Session, 
    articulo_id: int, 
    nuevo_precio: float, 
    tipo_precio: str,  # 'costo' o 'venta'
    usuario_id: Optional[int] = None,
    motivo: Optional[str] = None
) -> Articulos:
    """
    Función especializada para actualizar el precio de un artículo y registrar el cambio en el historial
    """
    try:
        # Obtener el artículo actual
        articulo = get_articulos(db, articulo_id)
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Artículo con ID {articulo_id} no encontrado"
            )
        
        # Definir qué campo se actualizará según el tipo de precio
        campo_precio = 'preciocosto' if tipo_precio == 'costo' else 'precioventa'
        precio_actual = articulo.preciocosto if tipo_precio == 'costo' else articulo.precioventa
        
        # Si el precio no ha cambiado, no hacemos nada
        if precio_actual == nuevo_precio:
            logger.info(f"El precio de {tipo_precio} del artículo {articulo_id} no ha cambiado")
            return articulo
            
        # Actualizar el precio
        datos_actualizacion = {campo_precio: nuevo_precio}
        articulo_actualizado = update_articulos(
            db=db, 
            id=articulo_id, 
            articulos_data=datos_actualizacion, 
            usuario_id=usuario_id, 
            motivo=motivo
        )
        
        logger.info(f"Precio de {tipo_precio} del artículo {articulo_id} actualizado: {precio_actual} -> {nuevo_precio}")
        return articulo_actualizado
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar precio de artículo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el precio: {str(e)}"
        )


def actualizar_precios_masivos(
    db: Session,
    filtro: Dict[str, Any],
    porcentaje: float,
    tipo_precio: str,  # 'costo' o 'venta'
    usuario_id: Optional[int] = None,
    motivo: Optional[str] = None
) -> int:
    """
    Actualiza los precios de múltiples artículos aplicando un porcentaje de variación
    y registra cada cambio en el historial
    """
    try:
        # Construir condiciones de filtro
        where_clause = ""
        params = {}
        
        if filtro:
            conditions = []
            for key, value in filtro.items():
                if key in ['id_tipo', 'marca', 'modelo']:
                    conditions.append(f"{key} = :{key}")
                    params[key] = value
            
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
        
        # Determinar qué campo de precio actualizar
        campo_precio = 'preciocosto' if tipo_precio == 'costo' else 'precioventa'
        
        # Construir la consulta para obtener los artículos que cumplen el filtro
        query = text(f"""
            SELECT id, {campo_precio} 
            FROM articulos 
            {where_clause}
        """)
        
        # Obtener los artículos a actualizar
        articulos = db.execute(query, params).fetchall()
        
        contador = 0
        for articulo in articulos:
            articulo_id = articulo[0]
            precio_actual = articulo[1] or 0
            
            # Calcular el nuevo precio aplicando el porcentaje
            nuevo_precio = precio_actual * (1 + porcentaje / 100)
            
            # Redondear a dos decimales para evitar imprecisiones
            nuevo_precio = round(nuevo_precio, 2)
            
            # Actualizar el precio individual y registrar en historial
            actualizar_precio_articulo(
                db=db,
                articulo_id=articulo_id,
                nuevo_precio=nuevo_precio,
                tipo_precio=tipo_precio,
                usuario_id=usuario_id,
                motivo=motivo or f"Actualización masiva de precios ({porcentaje}%)"
            )
            
            contador += 1
        
        return contador
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error en actualización masiva de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en actualización masiva de precios: {str(e)}"
        )


def get_articulos_stats(db: Session) -> Dict[str, Any]:
    """
    Obtiene estadísticas generales de los artículos para el dashboard
    
    Retorna:
    - total_articulos: Número total de artículos
    - cambios_precio_30_dias: Número de cambios de precio en los últimos 30 días
    - total_codigos_barras: Número de artículos con códigos de barras
    - total_codigos_qr: Número de artículos con códigos QR
    - continue_iteration: Bandera para preguntar al usuario si desea continuar con la iteración
    """
    try:
        stats = {}
        
        # Total de artículos
        result = db.execute(
            text("SELECT COUNT(*) FROM articulos")
        ).scalar()
        stats['total_articulos'] = result or 0
        
        # Cambios de precio en los últimos 30 días
        fecha_inicio = datetime.now() - timedelta(days=30)
        result = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM precios_historial 
                WHERE fecha_cambio >= :fecha_inicio
            """),
            {"fecha_inicio": fecha_inicio}
        ).scalar()
        stats['cambios_precio_30_dias'] = result or 0
        
        
        # Añadir bandera para preguntar si desea continuar con la iteración
        stats['continue_iteration'] = True
        stats['iteration_message'] = "¿Desea continuar con la iteración?"
        
        return stats
        
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener estadísticas de artículos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


def get_historial_precios(
    db: Session, 
    articulo_id: Optional[int] = None, 
    tipo_precio: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None, 
    fecha_fin: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de cambios de precios con filtros opcionales
    
    Args:
        db: Sesión de la base de datos
        articulo_id: ID del artículo (opcional)
        tipo_precio: Tipo de precio ('costo' o 'venta') (opcional)
        fecha_inicio: Fecha de inicio para filtrar (opcional)
        fecha_fin: Fecha de fin para filtrar (opcional)
        
    Returns:
        Lista de cambios de precios con datos del artículo
    """
    try:
        conditions = []
        params = {}
        
        # Construir condiciones de filtro
        if articulo_id:
            conditions.append("ph.articulo_id = :articulo_id")
            params['articulo_id'] = articulo_id
            
        if tipo_precio:
            conditions.append("ph.tipo_precio = :tipo_precio")
            params['tipo_precio'] = tipo_precio
            
        if fecha_inicio:
            conditions.append("ph.fecha_cambio >= :fecha_inicio")
            params['fecha_inicio'] = fecha_inicio
            
        if fecha_fin:
            conditions.append("ph.fecha_cambio <= :fecha_fin")
            params['fecha_fin'] = fecha_fin
        
        # Construir cláusula WHERE
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Query para obtener historial con datos de artículos
        query = text(f"""
            SELECT 
                ph.id,
                ph.articulo_id,
                a.codigo AS articulo_codigo,
                a.descripcion AS articulo_descripcion,
                ph.precio_anterior,
                ph.precio_nuevo,
                ph.tipo_precio,
                ph.fecha_cambio,
                ph.motivo
            FROM 
                precios_historial ph
                INNER JOIN articulos a ON ph.articulo_id = a.id

            {where_clause}
            ORDER BY ph.fecha_cambio DESC
        """)
        
        result = db.execute(query, params).fetchall()
        
        # Convertir resultado a lista de diccionarios
        historial = []
        for row in result:
            # Calcular variación porcentual
            precio_anterior = row[4] or 0
            precio_nuevo = row[5] or 0
            
            variacion_porcentual = 0
            if precio_anterior > 0:
                variacion_porcentual = ((precio_nuevo - precio_anterior) / precio_anterior) * 100
                
            cambio = {
                'id': row[0],
                'articulo_id': row[1],
                'articulo_codigo': row[2],
                'articulo_descripcion': row[3],
                'precio_anterior': precio_anterior,
                'precio_nuevo': precio_nuevo,
                'variacion_porcentual': round(variacion_porcentual, 2),
                'tipo_precio': row[6],
                'fecha_cambio': row[7].isoformat() if row[7] else None,
                'motivo': row[8]
            }
            
            historial.append(cambio)
            
        return historial
        
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener historial de precios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de precios: {str(e)}"
        )


def generar_codigo_barra(db: Session, articulo_id: int, tipo: str = "CODE128") -> Dict[str, Any]:
    """
    Genera un código de barras para un artículo
    
    Args:
        db: Sesión de la base de datos
        articulo_id: ID del artículo
        tipo: Tipo de código de barras (CODE128, EAN13, etc.)
        
    Returns:
        Diccionario con url de la imagen y código generado
    """
    try:
        # Verificar que el artículo existe
        articulo = get_articulos(db, articulo_id)
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artículo con ID {articulo_id} no encontrado"
            )
            
        # Crear directorio para códigos si no existe
        base_dir = "sql_app/static/app_stock/articulos/codigos"
        os.makedirs(base_dir, exist_ok=True)
        
        # Generar código único basado en el ID y código del artículo
        codigo = f"{articulo.codigo}-{articulo.id}" if articulo.codigo else str(articulo.id)
        
        # Elegir el tipo de código de barras
        if tipo == "EAN13":
            # EAN13 requiere exactamente 12 dígitos (el 13º es el dígito de control)
            codigo = codigo.replace("-", "").replace(" ", "")
            codigo = codigo[:12].zfill(12)
            barcode_class = barcode.get_barcode_class('ean13')
        else:
            # CODE128 por defecto, acepta cualquier caracter
            barcode_class = barcode.get_barcode_class('code128')
            
        # Generar el código de barras
        barcode_instance = barcode_class(codigo, writer=ImageWriter())
        
        # Guardar imagen y obtener ruta
        filename = f"{articulo_id}_{uuid.uuid4().hex}"
        filepath = os.path.join(base_dir, filename)
        fullpath = barcode_instance.save(filepath)
        
        # Obtener solo el nombre del archivo generado
        filename_with_ext = os.path.basename(fullpath)
        url = f"/static/app_stock/articulos/codigos/{filename_with_ext}"
        
        # Registrar el código en la base de datos (tabla articulos_codigos)
        query = text("""
            INSERT INTO articulos_codigos (articulo_id, tipo, codigo, url)
            VALUES (:articulo_id, 'barcode', :codigo, :url)
        """)
        
        db.execute(query, {
            "articulo_id": articulo_id,
            "codigo": codigo,
            "url": url
        })
        db.commit()
        
        return {
            "url": url,
            "codigo": codigo,
            "tipo": tipo
        }
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al generar código de barras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código de barras: {str(e)}"
        )


def generar_codigo_qr(db: Session, articulo_id: int, incluir_precio: bool = True) -> Dict[str, Any]:
    """
    Genera un código QR para un artículo
    
    Args:
        db: Sesión de la base de datos
        articulo_id: ID del artículo
        incluir_precio: Si se debe incluir el precio en el QR
        
    Returns:
        Diccionario con url de la imagen y datos codificados
    """
    try:
        # Verificar que el artículo existe
        articulo = get_articulos(db, articulo_id)
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artículo con ID {articulo_id} no encontrado"
            )
            
        # Crear directorio para códigos si no existe
        base_dir = "sql_app/static/app_stock/articulos/codigos"
        os.makedirs(base_dir, exist_ok=True)
        
        # Preparar datos para el código QR
        data = {
            "id": articulo.id,
            "codigo": articulo.codigo,
            "descripcion": articulo.descripcion
        }
        
        if incluir_precio:
            data["preciocosto"] = float(articulo.preciocosto) if articulo.preciocosto else 0
            data["precioventa"] = float(articulo.precioventa) if articulo.precioventa else 0
            
        # Convertir a formato de texto para el QR
        datos_str = str(data)
        
        # Crear el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(datos_str)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Generar nombre único para el archivo
        filename = f"qr_{articulo_id}_{uuid.uuid4().hex}.png"
        filepath = os.path.join(base_dir, filename)
        
        # Guardar la imagen
        img.save(filepath)
        
        # URL relativa para acceder a la imagen
        url = f"/static/app_stock/articulos/codigos/{filename}"
        
        # Registrar el código QR en la base de datos
        query = text("""
            INSERT INTO articulos_codigos (articulo_id, tipo, codigo, url)
            VALUES (:articulo_id, 'qr', :datos, :url)
        """)
        
        db.execute(query, {
            "articulo_id": articulo_id,
            "datos": datos_str,
            "url": url
        })
        db.commit()
        
        return {
            "url": url,
            "datos": datos_str
        }
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al generar código QR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar código QR: {str(e)}"
        )


def get_recent_price_changes(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Obtiene los cambios de precio más recientes
    
    Args:
        db: Sesión de la base de datos
        limit: Número máximo de registros a devolver
        
    Returns:
        Lista de cambios de precio recientes con información del artículo
    """
    try:
        # Construir la consulta SQL con la sintaxis correcta para TOP en SQL Server
        query_str = f"""
            SELECT TOP {limit}
                ph.id,
                ph.articulo_id,
                a.codigo AS articulo_codigo,
                a.descripcion AS articulo_descripcion,
                ph.precio_anterior,
                ph.precio_nuevo,
                ph.tipo_precio,
                ph.fecha_cambio,
                ph.motivo
            FROM 
                precios_historial ph
                INNER JOIN articulos a ON ph.articulo_id = a.id
            ORDER BY
                ph.fecha_cambio DESC
        """
        
        # Ejecutar la consulta
        result = db.execute(text(query_str)).fetchall()
        
        # Convertir resultado a lista de diccionarios
        cambios = []
        for row in result:
            # Calcular variación porcentual
            precio_anterior = row[4] or 0
            precio_nuevo = row[5] or 0
            
            variacion_porcentual = 0
            if precio_anterior > 0:
                variacion_porcentual = ((precio_nuevo - precio_anterior) / precio_anterior) * 100
                
            cambio = {
                'id': row[0],
                'articulo_id': row[1],
                'articulo_codigo': row[2],
                'articulo_descripcion': row[3],
                'precio_anterior': precio_anterior,
                'precio_nuevo': precio_nuevo,
                'variacion_porcentual': round(variacion_porcentual, 2),
                'tipo_precio': row[6],
                'fecha_cambio': row[7].isoformat() if row[7] else None,
                'motivo': row[8]
            }
            
            cambios.append(cambio)
            
        return cambios
        
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener cambios de precio recientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cambios de precio recientes: {str(e)}"
        )


def calcular_tiempo_transcurrido(fecha: datetime) -> str:
    """
    Calcula el tiempo transcurrido desde una fecha hasta ahora en formato legible
    
    Args:
        fecha: Fecha desde la que se calcula el tiempo
        
    Returns:
        String con el tiempo transcurrido (ej: "hace 3 horas", "hace 2 días")
    """
    if not fecha:
        return "fecha desconocida"
        
    ahora = datetime.now()
    diferencia = ahora - fecha
    
    # Convertir a segundos
    segundos = int(diferencia.total_seconds())
    
    # Menos de un minuto
    if segundos < 60:
        return "hace unos momentos"
        
    # Menos de una hora
    if segundos < 3600:
        minutos = segundos // 60
        return f"hace {minutos} {'minutos' if minutos > 1 else 'minuto'}"
        
    # Menos de un día
    if segundos < 86400:
        horas = segundos // 3600
        return f"hace {horas} {'horas' if horas > 1 else 'hora'}"
        
    # Menos de un mes (aproximadamente)
    if segundos < 2592000:  # 30 días
        dias = segundos // 86400
        return f"hace {dias} {'días' if dias > 1 else 'día'}"
        
    # Menos de un año
    if segundos < 31536000:  # 365 días
        meses = segundos // 2592000
        return f"hace {meses} {'meses' if meses > 1 else 'mes'}"
        
    # Más de un año
    años = segundos // 31536000
    return f"hace {años} {'años' if años > 1 else 'año'}"


def get_articulos_by_codigo(db: Session, codigo: str) -> Optional[Articulos]:
    """
    Obtiene un registro de artículos a partir de su código.
    """
    logger.info(f"Buscando Articulos con código = {codigo}")
    try:
        # Consulta SQL directa para buscar un artículo por su código
        result = db.execute(
            text("""
                SELECT id, codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo
                FROM articulos 
                WHERE codigo = :codigo
            """),
            {"codigo": codigo}
        ).first()
        
        if not result:
            logger.info(f"No se encontró ningún artículo con código {codigo}")
            return None
        
        articulo = Articulos()
        articulo.id = result[0]
        articulo.codigo = result[1]
        articulo.descripcion = result[2]
        articulo.preciocosto = result[3]
        articulo.precioventa = result[4]
        articulo.modelo = result[5]
        articulo.marca = result[6]
        articulo.id_tipo = result[7]
        
        return articulo
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar Articulos por código: {e}")
        return None

def get_historial_precios_por_articulo(
    db: Session,
    codigo_articulo: str,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de cambios de precios de un artículo específico por su código
    
    Args:
        db: Sesión de la base de datos
        codigo_articulo: Código del artículo
        fecha_inicio: Fecha inicial para filtrar (opcional)
        fecha_fin: Fecha final para filtrar (opcional)
        
    Returns:
        Lista de cambios de precios del artículo
    """
    try:
        # Primero obtenemos el ID del artículo por su código
        articulo = get_articulos_by_codigo(db, codigo_articulo)
        
        if not articulo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artículo con código {codigo_articulo} no encontrado"
            )
        
        # Usamos la función general de historial filtrando por el ID
        historial = get_historial_precios(
            db=db,
            articulo_id=articulo.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return historial
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener historial de precios por artículo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de precios por artículo: {str(e)}"
        )

def get_estadisticas_historial_precios(
    db: Session,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    tipo_precio: Optional[str] = None,
    filtro_articulo: Optional[str] = None,
    tipo_variacion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Obtiene estadísticas del historial de precios según los filtros aplicados
    
    Args:
        db: Sesión de la base de datos
        fecha_inicio: Fecha de inicio para filtrar (opcional)
        fecha_fin: Fecha de fin para filtrar (opcional)
        tipo_precio: Tipo de precio ('costo' o 'venta') (opcional)
        filtro_articulo: Código o descripción del artículo (opcional)
        tipo_variacion: Tipo de variación ('aumento', 'disminucion') (opcional)
        
    Returns:
        Diccionario con estadísticas del historial de precios
    """
    try:
        conditions = []
        params = {}
        
        # Construir condiciones de filtro
        if fecha_inicio:
            conditions.append("ph.fecha_cambio >= :fecha_inicio")
            params['fecha_inicio'] = fecha_inicio
            
        if fecha_fin:
            conditions.append("ph.fecha_cambio <= :fecha_fin")
            params['fecha_fin'] = fecha_fin
            
        if tipo_precio:
            conditions.append("ph.tipo_precio = :tipo_precio")
            params['tipo_precio'] = tipo_precio
        
        # Filtrar por artículo (código o descripción)
        if filtro_articulo:
            conditions.append("(a.codigo LIKE :filtro OR a.descripcion LIKE :filtro)")
            params['filtro'] = f"%{filtro_articulo}%"
        
        # Filtrar por tipo de variación (aumento o disminución)
        if tipo_variacion == 'aumento':
            conditions.append("ph.precio_nuevo > ph.precio_anterior")
        elif tipo_variacion == 'disminucion':
            conditions.append("ph.precio_nuevo < ph.precio_anterior")
        
        # Construir cláusula WHERE
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Consulta para obtener el recuento total
        query_total = text(f"""
            SELECT COUNT(*) 
            FROM precios_historial ph
            INNER JOIN articulos a ON ph.articulo_id = a.id
            {where_clause}
        """)
        
        total = db.execute(query_total, params).scalar() or 0
        
        # Si no hay registros, devolvemos estadísticas vacías
        if total == 0:
            return {
                "total": 0,
                "costo": 0,
                "venta": 0,
                "variacion_promedio": 0.0
            }
        
        # Consulta para contar los cambios por tipo de precio
        query_tipos = text(f"""
            SELECT tipo_precio, COUNT(*) as count
            FROM precios_historial ph
            INNER JOIN articulos a ON ph.articulo_id = a.id
            {where_clause}
            GROUP BY tipo_precio
        """)
        
        tipos_result = db.execute(query_tipos, params).fetchall()
        
        # Inicializar contadores por tipo
        costo_count = 0
        venta_count = 0
        
        # Procesar resultados por tipo
        for row in tipos_result:
            if row[0] == 'costo':
                costo_count = row[1]
            elif row[0] == 'venta':
                venta_count = row[1]
        
        # Calcular variación porcentual promedio
        query_variacion = text(f"""
            SELECT AVG(
                CASE 
                    WHEN ph.precio_anterior = 0 THEN 0
                    ELSE (ph.precio_nuevo - ph.precio_anterior) / ph.precio_anterior * 100
                END
            ) AS variacion_promedio
            FROM precios_historial ph
            INNER JOIN articulos a ON ph.articulo_id = a.id
            {where_clause}
        """)
        
        variacion_promedio = db.execute(query_variacion, params).scalar() or 0
        
        return {
            "total": total,
            "costo": costo_count,
            "venta": venta_count,
            "variacion_promedio": round(float(variacion_promedio), 2)
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener estadísticas del historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas del historial: {str(e)}"
        )

# Función auxiliar para el historial con filtros específicos
def get_historial_precios_con_filtros(
    db: Session,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    tipo_precio: Optional[str] = None,
    filtro_articulo: Optional[str] = None,
    tipo_variacion: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de precios con filtros adicionales para artículos y variación
    
    Args:
        db: Sesión de la base de datos
        fecha_inicio: Fecha de inicio para filtrar (opcional)
        fecha_fin: Fecha de fin para filtrar (opcional)
        tipo_precio: Tipo de precio ('costo' o 'venta') (opcional)
        filtro_articulo: Código o descripción del artículo (opcional)
        tipo_variacion: Tipo de variación ('aumento', 'disminucion') (opcional)
        
    Returns:
        Lista de registros del historial de precios que cumplen los filtros
    """
    try:
        conditions = []
        params = {}
        
        # Construir condiciones de filtro
        if fecha_inicio:
            conditions.append("ph.fecha_cambio >= :fecha_inicio")
            params['fecha_inicio'] = fecha_inicio
            
        if fecha_fin:
            conditions.append("ph.fecha_cambio <= :fecha_fin")
            params['fecha_fin'] = fecha_fin
            
        if tipo_precio:
            conditions.append("ph.tipo_precio = :tipo_precio")
            params['tipo_precio'] = tipo_precio
        
        # Filtrar por artículo (código o descripción)
        if filtro_articulo:
            conditions.append("(a.codigo LIKE :filtro OR a.descripcion LIKE :filtro)")
            params['filtro'] = f"%{filtro_articulo}%"
        
        # Filtrar por tipo de variación (aumento o disminución)
        if tipo_variacion == 'aumento':
            conditions.append("ph.precio_nuevo > ph.precio_anterior")
        elif tipo_variacion == 'disminucion':
            conditions.append("ph.precio_nuevo < ph.precio_anterior")
        
        # Construir cláusula WHERE
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Query para obtener historial con datos de artículos
        query = text(f"""
            SELECT 
                ph.id,
                ph.articulo_id,
                a.codigo AS codigo,
                a.descripcion AS descripcion,
                ph.precio_anterior,
                ph.precio_nuevo,
                ph.tipo_precio,
                ph.fecha_cambio,
                ph.motivo
            FROM 
                precios_historial ph
                INNER JOIN articulos a ON ph.articulo_id = a.id
            {where_clause}
            ORDER BY ph.fecha_cambio DESC
        """)
        
        result = db.execute(query, params).fetchall()
        
        # Convertir resultado a una lista de objetos que la API puede serializar
        historial = []
        for row in result:
            # Calcular variación porcentual
            precio_anterior = row[4] or 0
            precio_nuevo = row[5] or 0
            
            variacion_porcentual = 0
            if precio_anterior > 0:
                variacion_porcentual = ((precio_nuevo - precio_anterior) / precio_anterior) * 100
            
            # Crear objeto con atributos necesarios para la serialización
            cambio = type('HistorialPrecio', (), {
                'id': row[0],
                'articulo_id': row[1],
                'codigo': row[2],
                'descripcion': row[3],
                'precio_anterior': precio_anterior,
                'precio_nuevo': precio_nuevo,
                'variacion_porcentual': round(variacion_porcentual, 2),
                'tipo_precio': row[6],
                'fecha_cambio': row[7],
                'motivo': row[8]
            })
            
            historial.append(cambio)
        
        return historial
    
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener historial de precios con filtros: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de precios: {str(e)}"
        )