from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.productos import EcomerceProductos as Productos
from db.models.logs.activity_log import ActivityLog
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def log_activity(db: Session, user_id: int, action: str, description: str, request: Request):
    """
    Función auxiliar para registrar actividades del usuario en la tabla activity_log.
    Esta función está comentada por defecto y puede activarse según sea necesario.
    """
    # try:
    #     # Obtener IP del cliente
    #     client_ip = request.client.host if request.client else "unknown"
    #     
    #     # Obtener User-Agent
    #     user_agent = request.headers.get("user-agent", "unknown")
    #     
    #     # Crear registro de actividad
    #     activity = ActivityLog(
    #         usuario_id=user_id,
    #         accion=action,
    #         descripcion=description,
    #         ip_address=client_ip,
    #         user_agent=user_agent
    #     )
    #     
    #     db.add(activity)
    #     db.commit()
    #     
    # except Exception as e:
    #     logger.error(f"Error al registrar actividad: {e}")
    #     db.rollback()  # No fallar la operación principal por error de logging

def create_productos(db: Session, productos, user_data: dict = None, request: Request = None) -> Productos:
    """
    Crea un nuevo registro de Productos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos del producto (excluyendo PK autoincrement si aplica)
        if isinstance(productos, dict):
            productos_data = productos
        else:
            productos_data = {}
            for field in ['codigo', 'nombre', 'descripcion', 'id_categoria', 'precio', 'imagen_url', 'active']:
                if hasattr(productos, field):
                    productos_data[field] = getattr(productos, field)
        
        # Extraer variantes si existen
        variants_data = None
        if isinstance(productos, dict) and 'variants' in productos:
            variants_data = productos['variants']
        elif hasattr(productos, 'variants') and productos.variants:
            variants_data = productos.variants
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_productos (codigo, nombre, descripcion, id_categoria, precio, imagen_url, active)
            OUTPUT INSERTED.id, INSERTED.codigo, INSERTED.nombre, INSERTED.descripcion, INSERTED.id_categoria, INSERTED.precio, INSERTED.imagen_url, INSERTED.active
            VALUES (:codigo, :nombre, :descripcion, :id_categoria, :precio, :imagen_url, :active)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, productos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Productos con los valores devueltos
        new_productos = Productos()
        new_productos.id = row[0]
        new_productos.codigo = row[1]
        new_productos.nombre = row[2]
        new_productos.descripcion = row[3]
        new_productos.id_categoria = row[4]
        new_productos.precio = row[5]
        new_productos.imagen_url = row[6]
        new_productos.active = row[7]
        
        # Crear variantes si se proporcionaron
        if variants_data:
            for variant_data in variants_data:
                if isinstance(variant_data, dict):
                    variant_dict = variant_data
                else:
                    variant_dict = {}
                    for field in ['color', 'tipo', 'precio_adicional', 'stock', 'imagen_url', 'active']:
                        if hasattr(variant_data, field):
                            variant_dict[field] = getattr(variant_data, field)
                
                variant_dict['product_id'] = new_productos.id
                
                variant_query = text("""
                    INSERT INTO ecomerce_product_variants (product_id, color, tipo, precio_adicional, stock, imagen_url, active)
                    VALUES (:product_id, :color, :tipo, :precio_adicional, :stock, :imagen_url, :active)
                """)
                db.execute(variant_query, variant_dict)
            db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Productos (ID: {new_productos.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_productos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Productos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_productos(db: Session, id: int) -> Optional[Productos]:
    """
    Obtiene un registro de Productos por su clave primaria usando SQL directo.
    Incluye variantes del producto.
    """
    try:
        result = db.execute(
            text("SELECT id, codigo, nombre, descripcion, id_categoria, precio, imagen_url, active FROM ecomerce_productos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Productos no encontrado.")
        
        # Crear el objeto directamente con los valores
        productos = Productos()
        productos.id = result[0]
        productos.codigo = result[1]
        productos.nombre = result[2]
        productos.descripcion = result[3]
        productos.id_categoria = result[4]
        productos.precio = result[5]
        productos.imagen_url = result[6]
        productos.active = result[7]
        
        # Obtener variantes del producto
        variants_result = db.execute(
            text("SELECT id, product_id, color, tipo, precio_adicional, stock, imagen_url, active FROM ecomerce_product_variants WHERE product_id = :product_id"),
            {"product_id": id}
        ).fetchall()
        
        # Agregar variantes al objeto producto (como atributo dinámico)
        variants = []
        for variant_row in variants_result:
            # Crear un objeto simple para la variante
            class VariantObj:
                pass
            variant = VariantObj()
            variant.id = variant_row[0]
            variant.product_id = variant_row[1]
            variant.color = variant_row[2]
            variant.tipo = variant_row[3]
            variant.precio_adicional = variant_row[4]
            variant.stock = variant_row[5]
            variant.imagen_url = variant_row[6]
            variant.active = variant_row[7]
            variants.append(variant)
        
        productos.variants = variants
        
        return productos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_productos(db: Session) -> List[Productos]:
    """
    Obtiene una lista de todos los registros de Productos usando SQL directo.
    Incluye variantes de cada producto.
    """
    try:
        result = db.execute(
            text("SELECT id, codigo, nombre, descripcion, id_categoria, precio, imagen_url, active FROM ecomerce_productos")
        )
        
        productoss = []
        for row in result.fetchall():
            productos = Productos()
            productos.id = row[0]
            productos.codigo = row[1]
            productos.nombre = row[2]
            productos.descripcion = row[3]
            productos.id_categoria = row[4]
            productos.precio = row[5]
            productos.imagen_url = row[6]
            productos.active = row[7]
            
            # Obtener variantes del producto
            variants_result = db.execute(
                text("SELECT id, product_id, color, tipo, precio_adicional, stock, imagen_url, active FROM ecomerce_product_variants WHERE product_id = :product_id"),
                {"product_id": productos.id}
            ).fetchall()
            
            variants = []
            for variant_row in variants_result:
                # Crear un objeto simple para la variante
                class VariantObj:
                    pass
                variant = VariantObj()
                variant.id = variant_row[0]
                variant.product_id = variant_row[1]
                variant.color = variant_row[2]
                variant.tipo = variant_row[3]
                variant.precio_adicional = variant_row[4]
                variant.stock = variant_row[5]
                variant.imagen_url = variant_row[6]
                variant.active = variant_row[7]
                variants.append(variant)
            
            productos.variants = variants
            productoss.append(productos)
        
        return productoss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_productos(db: Session, id: int, user_data: dict = None, request: Request = None) -> Productos:
    """
    Elimina un registro de Productos por su clave primaria usando SQL directo.
    También elimina las variantes asociadas.
    """
    try:
        # Primero eliminar las variantes
        db.execute(text("DELETE FROM ecomerce_product_variants WHERE product_id = :product_id"), {"product_id": id})
        
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_productos 
                OUTPUT DELETED.id, DELETED.codigo, DELETED.nombre, DELETED.descripcion, DELETED.id_categoria, DELETED.precio, DELETED.imagen_url, DELETED.active
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Productos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_productos = Productos()
        deleted_productos.id = result[0]
        deleted_productos.codigo = result[1]
        deleted_productos.nombre = result[2]
        deleted_productos.descripcion = result[3]
        deleted_productos.id_categoria = result[4]
        deleted_productos.precio = result[5]
        deleted_productos.imagen_url = result[6]
        deleted_productos.active = result[7]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Productos (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_productos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_productos(db: Session, id: int, productos_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Productos:
    """
    Actualiza un registro de Productos por su clave primaria usando SQL directo.
    Maneja también la actualización de variantes.
    """
    logger.info(f"Actualizando Productos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_productos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Productos no encontrado.")
        
        # Separar datos de producto y variantes
        product_data_copy = productos_data.copy()
        variants_data = None
        
        if 'variants' in product_data_copy:
            variants_data = product_data_copy.pop('variants')
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        if 'id' in product_data_copy:
            del product_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not product_data_copy:
            return get_productos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in product_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_productos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.codigo, INSERTED.nombre, INSERTED.descripcion, INSERTED.id_categoria, INSERTED.precio, INSERTED.imagen_url, INSERTED.active
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = product_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Productos.")
        
        # Crear el objeto con los datos actualizados
        updated_productos = Productos()
        updated_productos.id = result[0]
        updated_productos.codigo = result[1]
        updated_productos.nombre = result[2]
        updated_productos.descripcion = result[3]
        updated_productos.id_categoria = result[4]
        updated_productos.precio = result[5]
        updated_productos.imagen_url = result[6]
        updated_productos.active = result[7]
        
        # Manejar variantes si se proporcionaron
        if variants_data is not None:
            # Para simplicidad, eliminar todas las variantes existentes y crear nuevas
            # En una implementación completa, se haría merge inteligente
            db.execute(text("DELETE FROM ecomerce_product_variants WHERE product_id = :product_id"), {"product_id": id})
            
            for variant_data in variants_data:
                if isinstance(variant_data, dict):
                    variant_dict = variant_data
                else:
                    variant_dict = {}
                    for field in ['color', 'tipo', 'precio_adicional', 'stock', 'imagen_url', 'active']:
                        if hasattr(variant_data, field):
                            variant_dict[field] = getattr(variant_data, field)
                
                variant_dict['product_id'] = id
                
                variant_query = text("""
                    INSERT INTO ecomerce_product_variants (product_id, color, tipo, precio_adicional, stock, imagen_url, active)
                    VALUES (:product_id, :color, :tipo, :precio_adicional, :stock, :imagen_url, :active)
                """)
                db.execute(variant_query, variant_dict)
            db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Productos (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return get_productos(db, id)  # Devolver con variantes incluidas
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Productos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
