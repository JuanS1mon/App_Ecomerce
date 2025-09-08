# Imports de bibliotecas estándar
from sql_app.Services.app_stock.articulos.model_confirmacion_movimiento import ConfirmacionMovimiento
from sql_app.Services.app_stock.stock.model_stock import Stock as StockModel
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
import logging

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class EstadoStock(Enum):
    """Estados de stock según ISO 9001 para trazabilidad"""
    DISPONIBLE = "disponible"
    RESERVADO = "reservado"
    EN_PREPARACION = "en_preparacion"
    BLOQUEADO_CALIDAD = "bloqueado_calidad"
    EN_TRANSITO = "en_transito"
    CUARENTENA = "cuarentena"
    
class TipoMovimiento(Enum):
    """Tipos de movimiento según mejores prácticas ERP"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    TRANSFERENCIA = "transferencia"
    AJUSTE_INVENTARIO = "ajuste_inventario"
    BLOQUEO_CALIDAD = "bloqueo_calidad"
    LIBERACION_CALIDAD = "liberacion_calidad"

def get_movimientos_pendientes(db: Session, mostrar_confirmados: bool = False) -> List[Dict[str, Any]]:
    """
    Obtiene los movimientos de stock pendientes de confirmación.
    Un movimiento pendiente tiene reservas o preparaciones mayores a 0.
    
    Args:
        db: Sesión de base de datos
        mostrar_confirmados: Si es True, muestra todos los movimientos; si es False, solo muestra los no confirmados
    """
    try:
        # Verificamos el tipo de dialecto de la base de datos
        dialect = db.bind.dialect.name
        logger.info(f"Dialect detected: {dialect}")
          # Construimos la condición WHERE según el parámetro mostrar_confirmados
        condicion_confirmado = "" if mostrar_confirmados else "AND (s.confirmado = 0 OR s.confirmado IS NULL)"
        
        # Usamos una consulta básica compatible con SQL Server y PostgreSQL
        movimientos = db.execute(text(f"""
            SELECT 
                s.nro_movimiento, 
                s.codigo_art,
                MIN(s.fecha) as fecha,
                SUM(s.cant_reservado) as total_reservado,
                SUM(s.cant_preparado) as total_preparado,
                MAX(s.id_articulos_serie) as id_articulos_serie,
                MAX(s.observacion) as observacion,                MAX(CASE WHEN s.confirmado IS NULL THEN 0 ELSE s.confirmado END) as confirmado
            FROM 
                stock s
            WHERE 
                (s.cant_reservado > 0 OR s.cant_preparado > 0) {condicion_confirmado}
            GROUP BY 
                s.nro_movimiento, s.codigo_art
            ORDER BY 
                s.nro_movimiento DESC
        """)).fetchall()
        
        # Procesamos los resultados de manera simplificada
        result = []
        for mov in movimientos:
            # Adaptamos la consulta según el dialecto
            if dialect == 'postgresql':
                limit_clause = "LIMIT 1"
            else:  # SQL Server y otros
                limit_clause = "TOP 1"
                
            # Obtenemos información del depósito origen (con preparado)
            origen_query = text(f"""
                SELECT {limit_clause} d.descripcion 
                FROM stock s 
                JOIN depositos d ON s.id_deposito = d.id
                WHERE s.nro_movimiento = :nro_movimiento 
                AND s.codigo_art = :codigo_art 
                AND s.cant_preparado > 0
            """)
            
            origen_result = db.execute(
                origen_query, 
                {"nro_movimiento": mov.nro_movimiento, "codigo_art": mov.codigo_art}
            ).fetchone()
            
            # Obtenemos información del depósito destino (con reservado)
            destino_query = text(f"""
                SELECT {limit_clause} d.descripcion 
                FROM stock s 
                JOIN depositos d ON s.id_deposito = d.id
                WHERE s.nro_movimiento = :nro_movimiento 
                AND s.codigo_art = :codigo_art 
                AND s.cant_reservado > 0
            """)
            
            destino_result = db.execute(
                destino_query, 
                {"nro_movimiento": mov.nro_movimiento, "codigo_art": mov.codigo_art}
            ).fetchone()
            
            # Extraemos las descripciones de depósitos
            origen_desc = origen_result[0] if origen_result else "Desconocido"
            destino_desc = destino_result[0] if destino_result else "Desconocido"            # Creamos el diccionario del movimiento
            movimiento_dict = {
                "nro_movimiento": mov.nro_movimiento,
                "codigo_art": mov.codigo_art,
                "fecha": mov.fecha,
                "total_reservado": mov.total_reservado,
                "total_preparado": mov.total_preparado,
                "id_articulos_serie": mov.id_articulos_serie,                "observacion": mov.observacion,
                "depositos": f"{origen_desc} → {destino_desc}",
                "confirmado": bool(getattr(mov, 'confirmado', 0) == 1),
                "deposito_origen": origen_desc,
                "deposito_destino": destino_desc
            }
            
            result.append(movimiento_dict)
            
        logger.info(f"Movimientos pendientes encontrados: {len(result)}")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener movimientos pendientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al obtener los movimientos pendientes: {str(e)}"
        )

def get_detalle_movimiento(db: Session, nro_movimiento: int, codigo_art: int) -> List[Dict[str, Any]]:
    """
    Obtiene el detalle de un movimiento específico por su número y código de artículo.
    """
    try:
        # La consulta es bastante estándar y debería funcionar en la mayoría de los motores de BD
        detalles = db.execute(text("""
            SELECT 
                s.id,
                s.nro_movimiento,
                s.codigo_art,
                s.id_deposito,
                d.descripcion as deposito_nombre,
                s.cant_disponible,
                s.cant_reservado,
                s.cant_preparado,
                s.fecha,
                s.observacion,
                a.descripcion as articulo_nombre
            FROM 
                stock s
            JOIN
                depositos d ON s.id_deposito = d.id
            LEFT JOIN
                articulos a ON s.codigo_art = a.id
            WHERE 
                s.nro_movimiento = :nro_movimiento AND s.codigo_art = :codigo_art
            ORDER BY 
                s.id
        """), {"nro_movimiento": nro_movimiento, "codigo_art": codigo_art}).fetchall()
        
        if not detalles:
            logger.warning(f"No se encontró detalle para movimiento={nro_movimiento}, codigo_art={codigo_art}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Movimiento no encontrado para nro_movimiento={nro_movimiento}, codigo_art={codigo_art}"
            )
            
        result = []
        for det in detalles:
            try:
                # Usamos getattr con valores predeterminados para evitar errores en caso de columnas faltantes
                detalle_dict = {
                    "id": getattr(det, 'id', 0),
                    "nro_movimiento": getattr(det, 'nro_movimiento', 0),
                    "codigo_art": getattr(det, 'codigo_art', 0),
                    "id_deposito": getattr(det, 'id_deposito', 0),
                    "deposito_nombre": getattr(det, 'deposito_nombre', "Desconocido"),
                    "cant_disponible": float(getattr(det, 'cant_disponible', 0)),
                    "cant_reservado": float(getattr(det, 'cant_reservado', 0)),
                    "cant_preparado": float(getattr(det, 'cant_preparado', 0)),
                    "fecha": getattr(det, 'fecha', None),
                    "observacion": getattr(det, 'observacion', ""),
                    "articulo_nombre": getattr(det, 'articulo_nombre', "Artículo sin nombre")
                }
                result.append(detalle_dict)
            except Exception as e:
                logger.error(f"Error al procesar detalle: {e}")
                # Continuamos con el siguiente detalle
            
        logger.info(f"Detalles encontrados para movimiento {nro_movimiento}: {len(result)}")
        return result
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error SQL al obtener detalle de movimiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al obtener el detalle del movimiento: {str(e)}"
        )

def confirmar_movimiento(
    db: Session, 
    nro_movimiento: int, 
    codigo_art: int, 
    cantidades: Dict[int, float] = None,
    completar_movimiento: bool = False,
    observacion: str = None
) -> Dict[str, Any]:
    """
    Confirma un movimiento de stock, ajustando las cantidades disponibles, reservadas y preparadas.
    
    Args:
        db: Sesión de base de datos
        nro_movimiento: Número de movimiento a confirmar
        codigo_art: Código del artículo
        cantidades: Diccionario opcional con cantidades a confirmar por depósito {'id_deposito': cantidad}
                    Si no se proporciona, se confirman todas las cantidades reservadas/preparadas        completar_movimiento: Si es True, marca el movimiento como completado después de confirmar
        observacion: Observación opcional para registrar con la confirmación
    """
    
    try:
        # Obtener los registros involucrados en el movimiento
        registros = db.query(StockModel).filter(
            and_(
                StockModel.nro_movimiento == nro_movimiento,
                StockModel.codigo_art == codigo_art,
                or_(
                    StockModel.cant_reservado > 0,
                    StockModel.cant_preparado > 0
                )
            )
        ).all()
        
        if not registros:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No se encontraron registros para confirmar con nro_movimiento={nro_movimiento}, codigo_art={codigo_art}"
            )
        
        # Identificar depósito origen y destino
        deposito_origen = None
        deposito_destino = None
        
        # Log de depuración para ver todos los registros
        logger.info(f"Registros a procesar en confirmar_movimiento: {len(registros)}")
        for i, reg in enumerate(registros):
            logger.info(f"Registro {i}: id_deposito={reg.id_deposito}, cant_preparado={reg.cant_preparado}, cant_reservado={reg.cant_reservado}")
          # Verificamos si tenemos depósitos 2 y 3 involucrados - caso especial
        deposito_2 = None
        deposito_3 = None
        for reg in registros:
            if reg.id_deposito == 2:
                deposito_2 = reg
                logger.info(f"Encontrado depósito 2 en el movimiento")
            elif reg.id_deposito == 3:
                deposito_3 = reg
                logger.info(f"Encontrado depósito 3 en el movimiento")
          # Si tenemos ambos depósitos, forzamos que el 3 sea origen y el 2 sea destino
        if deposito_2 and deposito_3:
            deposito_origen = deposito_3
            deposito_destino = deposito_2
            logger.info(f"Caso especial: Forzando depósito 3 como origen y depósito 2 como destino")
        else:
            # Primero intentamos identificar por cantidades positivas
            for reg in registros:
                if reg.cant_preparado > 0:  # El origen es el que tiene preparado positivo (el que envía)
                    deposito_origen = reg
                    logger.info(f"Depósito origen identificado por preparado positivo: {reg.id_deposito}")
                if reg.cant_reservado > 0:  # El destino es el que tiene reservado positivo (el que recibe)
                    deposito_destino = reg
                    logger.info(f"Depósito destino identificado por reservado positivo: {reg.id_deposito}")
        
        # Si no encontramos por criterios positivos, buscamos con criterios más amplios
        if not deposito_origen:
            # Buscar cualquier registro con cant_preparado diferente de 0
            for reg in registros:
                if reg.cant_preparado != 0:
                    deposito_origen = reg
                    logger.info(f"Depósito origen identificado por preparado no cero: {reg.id_deposito}")
                    break
            
            # Si aún no hay origen, intentamos identificarlo por disponible negativo
            if not deposito_origen:
                for reg in registros:
                    if reg.cant_disponible < 0:                        # Si hay un registro con disponible negativo, tenemos que verificar
                        if reg.cant_reservado > 0 and len(registros) == 2:
                            # Si este depósito tiene reservado positivo, probablemente sea el destino
                            # El origen debería ser el otro depósito
                            for otro_reg in registros:
                                if otro_reg.id_deposito != reg.id_deposito:
                                    deposito_origen = otro_reg
                                    logger.info(f"Depósito origen inferido por disponible negativo: {deposito_origen.id_deposito}")
                                    # Registrar los valores específicos para diagnóstico
                                    logger.info(f"Depósito disponible negativo: {reg.id_deposito}, "
                                               f"disponible={reg.cant_disponible}, reservado={reg.cant_reservado}, "
                                               f"preparado={reg.cant_preparado}")
                                    logger.info(f"Depósito origen inferido: {deposito_origen.id_deposito}, "
                                               f"disponible={deposito_origen.cant_disponible}, reservado={deposito_origen.cant_reservado}, "
                                               f"preparado={deposito_origen.cant_preparado}")
                                    break
                        break
        
        if not deposito_destino:
            # Buscar cualquier registro con cant_reservado diferente de 0
            for reg in registros:
                if reg.cant_reservado != 0:
                    deposito_destino = reg
                    break
        
        # Si todavía no tenemos uno de los depósitos, tomamos el opuesto del que sí tenemos
        if deposito_origen and not deposito_destino:
            # Si solo tenemos origen pero no destino, buscamos el otro registro
            for reg in registros:
                if reg.id_deposito != deposito_origen.id_deposito:
                    deposito_destino = reg
                    logger.info(f"Inferido destino por exclusión: {deposito_destino.id_deposito}")
                    break
        
        if not deposito_origen and deposito_destino:
            # Si solo tenemos destino pero no origen, buscamos el otro registro
            for reg in registros:
                if reg.id_deposito != deposito_destino.id_deposito:
                    deposito_origen = reg
                    logger.info(f"Inferido origen por exclusión: {deposito_origen.id_deposito}")
                    break
                      # Log de depuración para ver qué depósitos se identificaron
        logger.info(f"Depósito origen identificado: {deposito_origen.id_deposito if deposito_origen else None}")
        logger.info(f"Depósito destino identificado: {deposito_destino.id_deposito if deposito_destino else None}")

        if not deposito_origen or not deposito_destino:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se pudo identificar claramente el depósito origen y destino"
            )        
        
        # Determinar la cantidad a transferir
        # Usar valores absolutos para el cálculo
        cantidad_preparada = abs(deposito_origen.cant_preparado) if deposito_origen.cant_preparado else 0
        cantidad_reservada = abs(deposito_destino.cant_reservado) if deposito_destino.cant_reservado else 0
        
        logger.info(f"Cantidad preparada (abs): {cantidad_preparada}, Cantidad reservada (abs): {cantidad_reservada}")
        
        # Determinar la cantidad a confirmar basada en los valores absolutos
        if cantidad_preparada > 0 and cantidad_reservada > 0:
            # Si ambos valores son positivos, usamos el mínimo
            cantidad_confirmar = min(cantidad_preparada, cantidad_reservada)
            logger.info(f"Usando el mínimo entre preparado y reservado: {cantidad_confirmar}")
        elif cantidad_preparada > 0:
            # Si solo hay preparado, usamos esa cantidad
            cantidad_confirmar = cantidad_preparada
            logger.info(f"Usando solo cantidad preparada: {cantidad_confirmar}")
        elif cantidad_reservada > 0:
            # Si solo hay reservado, usamos esa cantidad
            cantidad_confirmar = cantidad_reservada
            logger.info(f"Usando solo cantidad reservada: {cantidad_confirmar}")
        else:        # Si no hay ni preparado ni reservado, inicialmente no hay cantidad para confirmar
            cantidad_confirmar = 0
            logger.info("No hay cantidades válidas para confirmar desde preparado/reservado, revisando caso especial")# Si se proporcionó una cantidad específica por el usuario, la usamos (sin exceder la calculada)        if cantidades y deposito_origen.id_deposito in cantidades:
            cantidad_especifica = float(cantidades.get(deposito_origen.id_deposito, 0))
            logger.info(f"Cantidad específica proporcionada: {cantidad_especifica}")

            if cantidad_confirmar > 0:
                # Validamos que la cantidad específica no sea mayor que la calculada
                if cantidad_especifica > cantidad_confirmar and not (deposito_2 and deposito_3):
                    # Solo aplicamos esta validación si NO es el caso especial de depósitos 2 y 3
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"La cantidad a confirmar ({cantidad_especifica}) no puede exceder la cantidad disponible ({cantidad_confirmar})"
                    )
                # Permitimos confirmar una cantidad menor para dejar el resto pendiente
                cantidad_confirmar = cantidad_especifica
                logger.info(f"Usando cantidad específica proporcionada: {cantidad_confirmar}")            
            elif cantidad_especifica > 0:
                # Si hay una cantidad específica y es válida, la usamos
                # Solo para el caso especial de los depósitos 2 y 3
                if deposito_2 and deposito_3:
                    logger.info(f"Caso especial: Usando cantidad específica para depósitos 2 y 3: {cantidad_especifica}")
                    cantidad_confirmar = cantidad_especifica
                else:
                    # Para otros depósitos, validamos que haya cantidades disponibles
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No hay cantidades disponibles para confirmar"
                    )
            else:
                # Si la cantidad específica es 0 o negativa
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La cantidad específica a confirmar debe ser mayor que cero"
                )    
            logger.info(f"Cantidad final después de aplicar específica: {cantidad_confirmar}")        # Validar que la cantidad sea válida antes de proceder
        if cantidad_confirmar <= 0:
            # Caso especial - si estamos en el caso de depósitos 2 y 3 con cantidad específica, permitir continuar
            if deposito_2 and deposito_3 and cantidades and deposito_origen.id_deposito in cantidades:
                cantidad_especifica = float(cantidades.get(deposito_origen.id_deposito, 0))
                if cantidad_especifica > 0:
                    logger.info(f"Caso especial depósitos 2 y 3: Permitiendo confirmar {cantidad_especifica} a pesar de no tener cantidades válidas iniciales")
                    cantidad_confirmar = cantidad_especifica
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="La cantidad específica debe ser mayor que cero para el caso especial"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="No hay cantidad válida para confirmar"
                )        # Guardamos los valores originales antes de cualquier modificación
        # para asegurar que estén disponibles para todos los flujos de ejecución
        # Usamos variables de instancia para facilitar el acceso en caso de excepciones
        disponible_origen_original = deposito_origen.cant_disponible
        disponible_destino_original = deposito_destino.cant_disponible
        logger.info(f"Valores originales guardados: origen={disponible_origen_original}, destino={disponible_destino_original}")
        
        # MEJORA: Calcular el stock disponible real utilizando el enfoque SAP
        stock_origen_calculado = calcular_stock_disponible(db, deposito_origen.id_deposito, codigo_art)
        disponible_real = stock_origen_calculado["disponible"]
        
        # Verificar si hay suficiente stock disponible calculado en tiempo real
        if disponible_real < cantidad_confirmar and not (deposito_2 and deposito_3):
            # Solo aplicamos esta validación si NO es el caso especial de depósitos 2 y 3
            logger.warning(f"Stock insuficiente según cálculo en tiempo real: disponible={disponible_real}, "
                         f"cantidad a confirmar={cantidad_confirmar}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock disponible insuficiente según cálculo en tiempo real. Disponible: {disponible_real}, "
                      f"Cantidad a confirmar: {cantidad_confirmar}"
            )
        
        # Verificar si es una confirmación parcial
        es_parcial = (cantidad_confirmar < cantidad_preparada) or (cantidad_confirmar < cantidad_reservada)
          
        # Si completar_movimiento es True, forzamos el estado a completo independientemente de las cantidades
        if completar_movimiento:
            logger.info(f"Forzando completar movimiento por parámetro completar_movimiento=True")
            es_parcial = False
              
        # Usar la observación proporcionada si existe
        observacion_texto = observacion if observacion else f"Confirmación {'parcial' if es_parcial else 'completa'} de movimiento #{nro_movimiento}: {cantidad_confirmar} unidades"
        
        if es_parcial:
            # Agregar estos logs antes de la confirmación parcial
            logger.info(f"Confirmación PARCIAL - Valores antes de actualizar:")
            logger.info(f"Origen (ID {deposito_origen.id_deposito}): disponible={disponible_origen_original}, preparado={deposito_origen.cant_preparado}")
            logger.info(f"Destino (ID {deposito_destino.id_deposito}): disponible={disponible_destino_original}, reservado={deposito_destino.cant_reservado}")
            logger.info(f"Cantidad a confirmar: {cantidad_confirmar} de {cantidad_preparada} preparado / {cantidad_reservada} reservado")            # En confirmación parcial, solo ajustamos las cantidades preparadas y reservadas
            # en los registros originales, pero NO modificamos el disponible
            deposito_origen.cant_preparado -= cantidad_confirmar
            deposito_destino.cant_reservado -= cantidad_confirmar
            
            # Los valores originales ya fueron guardados previamente, no es necesario volver a guardarlos aquí
            
            # Crear registros nuevos para la parte confirmada con el nuevo disponible
            nuevo_origen = StockModel(
                nro_movimiento=nro_movimiento,
                codigo_art=codigo_art,
                id_articulos_serie=deposito_origen.id_articulos_serie,
                id_deposito=deposito_origen.id_deposito,
                cant_disponible=disponible_origen_original - cantidad_confirmar,  # Nuevo disponible calculado
                cant_reservado=0,  # No debería haber reservas en el origen
                cant_preparado=0,  # El preparado restante debe estar en el registro original
                tipo=True,
                confirmado=True,
                fecha=deposito_origen.fecha,
                observacion=f"{observacion_texto} (Parcial: {cantidad_confirmar} de {cantidad_preparada})",
                anulado=False
            )
            nuevo_destino = StockModel(
                nro_movimiento=nro_movimiento,
                codigo_art=codigo_art,
                id_articulos_serie=deposito_destino.id_articulos_serie,
                id_deposito=deposito_destino.id_deposito,
                cant_disponible=disponible_destino_original + cantidad_confirmar,  # Nuevo disponible calculado
                cant_reservado=0,  # La reserva restante debe estar en el registro original
                cant_preparado=0,  # No debería haber preparado en el destino
                tipo=True,
                confirmado=True,
                fecha=deposito_destino.fecha,                observacion=f"{observacion_texto} (Parcial: {cantidad_confirmar} de {cantidad_reservada})",
                anulado=False
            )
            db.add(nuevo_origen)
            db.add(nuevo_destino)
            db.commit()
            
            # Logs después de crear los nuevos registros
            logger.info(f"Confirmación PARCIAL - Nuevos registros creados:")
            logger.info(f"Origen (ID {nuevo_origen.id_deposito}): disponible={nuevo_origen.cant_disponible}, preparado={nuevo_origen.cant_preparado}")
            logger.info(f"Destino (ID {nuevo_destino.id_deposito}): disponible={nuevo_destino.cant_disponible}, reservado={nuevo_destino.cant_reservado}")
            logger.info(f"Registros originales después de actualizar:")
            logger.info(f"Origen (ID {deposito_origen.id_deposito}): disponible={deposito_origen.cant_disponible}, preparado={deposito_origen.cant_preparado}")
            logger.info(f"Destino (ID {deposito_destino.id_deposito}): disponible={deposito_destino.cant_disponible}, reservado={deposito_destino.cant_reservado}")
            
            return {
                "mensaje": "Movimiento parcialmente confirmado. El resto queda pendiente.",
                "nro_movimiento": nro_movimiento,
                "codigo_art": codigo_art,
                "cantidad_confirmada": cantidad_confirmar,
                "estado": "parcial",
                "origen": {
                    "id_deposito": deposito_origen.id_deposito,
                    "cant_disponible_nueva": disponible_origen_original - cantidad_confirmar,  # Nuevo disponible calculado
                    "cant_disponible_anterior": disponible_origen_original,  # Disponible original sin modificar
                    "cant_preparado_restante": deposito_origen.cant_preparado,
                    "cant_preparado_confirmado": cantidad_confirmar,
                    "porcentaje_confirmado": round((cantidad_confirmar / (deposito_origen.cant_preparado + cantidad_confirmar)) * 100, 2),
                    "movimiento_stock": cantidad_confirmar  # Valor de la mercadería movida
                },
                "destino": {
                    "id_deposito": deposito_destino.id_deposito,
                    "cant_disponible_nueva": disponible_destino_original + cantidad_confirmar,  # Nuevo disponible calculado
                    "cant_disponible_anterior": disponible_destino_original,  # Disponible original sin modificar
                    "cant_reservado_restante": deposito_destino.cant_reservado,
                    "cant_reservado_confirmado": cantidad_confirmar,
                    "porcentaje_confirmado": round((cantidad_confirmar / (deposito_destino.cant_reservado + cantidad_confirmar)) * 100, 2),
                    "movimiento_stock": cantidad_confirmar  # Valor de la mercadería movida
                },
                "fecha_confirmacion_parcial": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
              # Para confirmación completa
        # Los valores originales ya fueron guardados previamente
        
        # NO modificamos los disponibles en los registros originales
        # Solo creamos nuevos registros con los valores actualizados
        
        # Crear registros nuevos para la cantidad que se confirma
        # Actualizar deposito origen (el que tiene preparado)
        nuevo_origen = StockModel(
            nro_movimiento=nro_movimiento,  # Mantenemos el mismo número de movimiento
            codigo_art=codigo_art,
            id_articulos_serie=deposito_origen.id_articulos_serie,
            id_deposito=deposito_origen.id_deposito,
            cant_disponible=disponible_origen_original - cantidad_confirmar,  # Calculamos el nuevo disponible
            cant_reservado=0,  # No hay cantidad reservada en el origen
            cant_preparado=max(0, deposito_origen.cant_preparado - cantidad_confirmar),  # Calculamos lo que queda de preparado
            tipo=True,  # Marcamos como confirmado
            confirmado=True,  # Marcar como confirmado
            fecha=deposito_origen.fecha,
            observacion=observacion_texto,
            anulado=False        
        )
        
        # Modificación para nuevo_destino - cálculo del cant_reservado
        nuevo_destino = StockModel(
            nro_movimiento=nro_movimiento,  # Mantenemos el mismo número de movimiento
            codigo_art=codigo_art,
            id_articulos_serie=deposito_destino.id_articulos_serie,
            id_deposito=deposito_destino.id_deposito,
            cant_disponible=disponible_destino_original + cantidad_confirmar,  # Calculamos el nuevo disponible
            cant_reservado=max(0, deposito_destino.cant_reservado - cantidad_confirmar),  # Calculamos lo que queda de reservado
            cant_preparado=0,  # No hay cantidad preparada en el destino
            tipo=True,  # Marcamos como confirmado
            confirmado=True,  # Marcar como confirmado
            fecha=deposito_destino.fecha,
            observacion=observacion_texto,
            anulado=False
        )
        db.add(nuevo_origen)
        db.add(nuevo_destino)
        # Actualizar los registros originales
        # Para una confirmación completa, solo marcamos los registros como confirmados
        # sin modificar sus valores originales
        for reg in registros:
            reg.confirmado = True
            # No modificamos cant_preparado y cant_reservado para preservar el historial

        db.commit()

        logger.info(f"Origen (ID {deposito_origen.id_deposito}): disponible={deposito_origen.cant_disponible}, preparado={deposito_origen.cant_preparado}")
        logger.info(f"Destino (ID {deposito_destino.id_deposito}): disponible={deposito_destino.cant_disponible}, reservado={deposito_destino.cant_reservado}")

        # Establecer el mensaje basado en si es una confirmación parcial o completa
        mensaje_confirmacion = "Movimiento completamente confirmado." if not es_parcial else "Movimiento parcialmente confirmado."

        return {
            "mensaje": mensaje_confirmacion,
            "nro_movimiento_original": nro_movimiento,
            "nro_movimiento_confirmacion": nro_movimiento,  # Devolvemos el mismo número de movimiento
            "codigo_art": codigo_art,
            "cantidad_confirmada": cantidad_confirmar,
            "estado": "parcial" if es_parcial else "completo",
            "origen": {
                "id_deposito": deposito_origen.id_deposito,
                "cant_disponible_anterior": disponible_origen_original,  # Disponible original sin modificar
                "cant_disponible_nueva": disponible_origen_original - cantidad_confirmar,  # Calculamos el nuevo disponible
                "cant_preparado_anterior": deposito_origen.cant_preparado + (cantidad_confirmar if es_parcial else 0),
                "cant_preparado_nueva": deposito_origen.cant_preparado,
                "movimiento_stock": cantidad_confirmar  # Valor de la mercadería movida
            },
            "destino": {
                "id_deposito": deposito_destino.id_deposito,
                "cant_disponible_anterior": disponible_destino_original,  # Disponible original sin modificar
                "cant_disponible_nueva": disponible_destino_original + cantidad_confirmar,  # Calculamos el nuevo disponible
                "cant_reservado_anterior": deposito_destino.cant_reservado + (cantidad_confirmar if es_parcial else 0),
                "cant_reservado_nueva": deposito_destino.cant_reservado,
                "movimiento_stock": cantidad_confirmar  # Valor de la mercadería movida
            }        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado en confirmar_movimiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al confirmar el movimiento: {str(e)}"
        )

def revertir_confirmacion(db: Session, nro_movimiento: int, codigo_art: int) -> Dict[str, Any]:
    """
    Revierte la confirmación de un movimiento de stock, cambiando el estado de confirmado a no confirmado.
    
    Args:
        db: Sesión de base de datos
        nro_movimiento: Número de movimiento a revertir
        codigo_art: Código del artículo
    
    Returns:
        Un diccionario con el resultado de la operación
    """
    try:
        # Verificar que existen registros para este movimiento
        registros = db.query(StockModel).filter(
            and_(
                StockModel.nro_movimiento == nro_movimiento,
                StockModel.codigo_art == codigo_art
            )
        ).all()
        
        if not registros:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No se encontraron registros para el movimiento nro_movimiento={nro_movimiento}, codigo_art={codigo_art}"
            )
        
        # Contar cuántos registros están confirmados
        registros_confirmados = sum(1 for reg in registros if getattr(reg, 'confirmado', False))
        
        if registros_confirmados == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"El movimiento nro_movimiento={nro_movimiento}, codigo_art={codigo_art} no está confirmado"
            )
        
        # Actualizar todos los registros de este movimiento para cambiar confirmado a False
        for registro in registros:
            registro.confirmado = False
        
        db.commit()
        
        return {
            "mensaje": "Se ha revertido la confirmación del movimiento correctamente",
            "nro_movimiento": nro_movimiento,
            "codigo_art": codigo_art,
            "registros_actualizados": len(registros)
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al revertir confirmación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al revertir confirmación: {str(e)}"
        )

def cerrar_movimiento(db: Session, nro_movimiento: int, codigo_art: int) -> Dict[str, Any]:
    """
    Cierra un movimiento de stock incluso si falta mercadería, marcándolo como completado manualmente.

    Args:
        db: Sesión de base de datos
        nro_movimiento: Número de movimiento a cerrar
        codigo_art: Código del artículo

    Returns:
        Un diccionario con el resultado de la operación
    """
    try:
        # Verificar que existen registros para este movimiento
        registros = db.query(StockModel).filter(
            and_(
                StockModel.nro_movimiento == nro_movimiento,
                StockModel.codigo_art == codigo_art
            )
        ).all()

        if not registros:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No se encontraron registros para el movimiento nro_movimiento={nro_movimiento}, codigo_art={codigo_art}"
            )

        # Marcar todos los registros como confirmados
        for registro in registros:
            registro.confirmado = True

        db.commit()

        return {
            "mensaje": "El movimiento se ha cerrado manualmente.",
            "nro_movimiento": nro_movimiento,
            "codigo_art": codigo_art,
            "registros_actualizados": len(registros)
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al cerrar movimiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al cerrar movimiento: {str(e)}"
        )
def calcular_stock_disponible(db: Session, id_deposito: int, codigo_art: int, incluir_auditoria: bool = False) -> Dict[str, Any]:
    """
    Calcula el stock disponible en tiempo real para un artículo en un depósito específico,
    siguiendo el enfoque de SAP ERP y normas ISO 9001 para trazabilidad completa.
    
    Formula SAP: Stock Disponible = Stock Físico - Reservas - En Preparación - Bloqueados por Calidad
    
    Mejoras ISO 9001:
    - Validación de consistencia de datos
    - Trazabilidad completa de cálculos
    - Control de calidad en tiempo real
    - Auditoría de movimientos
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        incluir_auditoria: Si incluir información de auditoría detallada
        
    Returns:
        Diccionario con desglose detallado del stock y metadatos de calidad:
        {
            "fisico": valor del stock físico,
            "reservado": valor total reservado,
            "preparado": valor total en preparación,  
            "bloqueado": valor bloqueado por calidad,
            "disponible": valor disponible calculado,
            "metadatos": información de auditoría y validación (si se solicita)
        }
    """
    try:
        # Obtenemos el último registro para este artículo en este depósito
        ultimo_registro = db.query(StockModel).filter(
            and_(
                StockModel.id_deposito == id_deposito,
                StockModel.codigo_art == codigo_art
            )
        ).order_by(StockModel.id.desc()).first()
        
        if not ultimo_registro:
            return {
                "fisico": 0.0,
                "reservado": 0.0,
                "preparado": 0.0,
                "bloqueado": 0.0,
                "disponible": 0.0
            }
        
        # Stock físico almacenado (lo que tenemos en la BD como disponible)
        stock_fisico = ultimo_registro.cant_disponible
        
        # Sumamos todas las reservas activas para este artículo en este depósito
        reservas = db.query(func.sum(StockModel.cant_reservado)).filter(
            and_(
                StockModel.id_deposito == id_deposito,
                StockModel.codigo_art == codigo_art,
                StockModel.cant_reservado > 0,
                or_(
                    StockModel.confirmado == False,
                    StockModel.confirmado == None
                )
            )
        ).scalar() or 0.0
        
        # Sumamos todas las preparaciones activas para este artículo en este depósito
        preparaciones = db.query(func.sum(StockModel.cant_preparado)).filter(
            and_(
                StockModel.id_deposito == id_deposito,
                StockModel.codigo_art == codigo_art,
                StockModel.cant_preparado > 0,
                or_(
                    StockModel.confirmado == False,
                    StockModel.confirmado == None
                )
            )
        ).scalar() or 0.0
        
        # Obtenemos bloqueos por calidad activos para este artículo en este depósito
        # Primero importamos el modelo si es necesario
        try:
            from sql_app.Services.app_stock.articulos.model_calidad import CalidadBloqueo
            
            # Sumamos todas las cantidades bloqueadas activas
            bloqueados_calidad = db.query(func.sum(CalidadBloqueo.cantidad)).filter(
                and_(
                    CalidadBloqueo.id_deposito == id_deposito,
                    CalidadBloqueo.codigo_art == codigo_art,
                    CalidadBloqueo.activo == True
                )
            ).scalar() or 0.0
            
        except ImportError:
            # Si el modelo no está disponible, asumimos que no hay bloqueos
            logger.warning("Modelo CalidadBloqueo no disponible, se asume 0 en bloqueos por calidad")
            bloqueados_calidad = 0.0
          # Calculamos el stock disponible real
        disponible = stock_fisico - reservas - preparaciones - bloqueados_calidad
        
        # Validaciones ISO 9001 para asegurar integridad
        alertas_calidad = []
        
        # Alerta si stock disponible es negativo
        if disponible < 0:
            alertas_calidad.append({
                "tipo": "stock_negativo",
                "mensaje": f"Stock disponible negativo: {disponible}",
                "requiere_accion": True
            })
        
        # Alerta si reservas exceden stock físico
        if reservas > stock_fisico:
            alertas_calidad.append({
                "tipo": "sobre_reserva",
                "mensaje": f"Reservas ({reservas}) exceden stock físico ({stock_fisico})",
                "requiere_accion": True
            })
        
        # Alerta si hay mucho stock bloqueado por calidad
        porcentaje_bloqueado = (bloqueados_calidad / stock_fisico * 100) if stock_fisico > 0 else 0
        if porcentaje_bloqueado > 20:  # Más del 20% bloqueado es una alerta
            alertas_calidad.append({
                "tipo": "alto_bloqueo_calidad",
                "mensaje": f"{porcentaje_bloqueado:.1f}% del stock está bloqueado por calidad",
                "requiere_accion": False
            })
        
        # Registramos información detallada para diagnóstico y auditoría ISO
        logger.info(f"Stock calculado para depósito {id_deposito}, artículo {codigo_art}: "
                    f"físico={stock_fisico}, reservas={reservas}, preparaciones={preparaciones}, "
                    f"bloqueados={bloqueados_calidad}, disponible={disponible}")
        
        # Resultado base
        resultado = {
            "fisico": float(stock_fisico),
            "reservado": float(reservas),
            "preparado": float(preparaciones),
            "bloqueado": float(bloqueados_calidad),
            "disponible": float(disponible)
        }
        
        # Agregar metadatos de auditoría si se solicita
        if incluir_auditoria:
            resultado["metadatos"] = {
                "fecha_calculo": datetime.now().isoformat(),
                "ultimo_movimiento_id": ultimo_registro.id if ultimo_registro else None,
                "alertas_calidad": alertas_calidad,
                "cumple_iso": len([a for a in alertas_calidad if a["requiere_accion"]]) == 0,
                "porcentaje_disponible": (disponible / stock_fisico * 100) if stock_fisico > 0 else 0,
                "rotacion_stock": {
                    "reservas_activas": reservas > 0,
                    "preparaciones_activas": preparaciones > 0,
                    "bloqueos_activos": bloqueados_calidad > 0
                }
            }
        
        # Devolvemos el resultado completo
        return resultado
    except SQLAlchemyError as e:
        logger.error(f"Error al calcular stock disponible: {e}")
        return {
            "fisico": 0.0,
            "reservado": 0.0,
            "preparado": 0.0,
            "bloqueado": 0.0,
            "disponible": 0.0
        }

def get_historial_confirmaciones(db: Session, nro_movimiento: int, codigo_art: int) -> List[Dict[str, Any]]:
    # Implementación de la función para obtener el historial de confirmaciones
    historial = db.query(ConfirmacionMovimiento).filter(
        ConfirmacionMovimiento.nro_movimiento == nro_movimiento,
        ConfirmacionMovimiento.codigo_art == codigo_art
    ).all()

    return [
        {
            "fecha": confirmacion.fecha,
            "cantidad": confirmacion.cantidad,
            "estado": confirmacion.estado
        }
        for confirmacion in historial
    ]

def validar_consistencia_stock(db: Session, id_deposito: int, codigo_art: int) -> Dict[str, Any]:
    """
    Valida la consistencia del stock según normas ISO 9001 para asegurar 
    la integridad de los datos y trazabilidad completa.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito
        codigo_art: Código del artículo
        
    Returns:
        Diccionario con el resultado de la validación
    """
    try:
        inconsistencias = []
        warnings = []
        
        # Obtener stock calculado actual
        stock_calculado = calcular_stock_disponible(db, id_deposito, codigo_art)
        
        # Validación 1: Stock disponible no puede ser negativo (norma ISO 9001)
        if stock_calculado["disponible"] < 0:
            inconsistencias.append({
                "tipo": "stock_negativo",
                "mensaje": f"Stock disponible negativo: {stock_calculado['disponible']}",
                "criticidad": "alta"
            })
        
        # Validación 2: Verificar coherencia de movimientos
        movimientos_inconsistentes = db.execute(text("""
            SELECT nro_movimiento, COUNT(*) as cantidad
            FROM stock 
            WHERE id_deposito = :id_deposito AND codigo_art = :codigo_art
            GROUP BY nro_movimiento
            HAVING COUNT(*) = 1
        """), {"id_deposito": id_deposito, "codigo_art": codigo_art}).fetchall()
        
        if movimientos_inconsistentes:
            warnings.append({
                "tipo": "movimientos_huerfanos",
                "mensaje": f"Se encontraron {len(movimientos_inconsistentes)} movimientos sin par entrada/salida",
                "criticidad": "media"
            })
        
        # Validación 3: Verificar reservas vs stock físico
        if stock_calculado["reservado"] > stock_calculado["fisico"]:
            inconsistencias.append({
                "tipo": "reservas_excesivas",
                "mensaje": f"Reservas ({stock_calculado['reservado']}) exceden stock físico ({stock_calculado['fisico']})",
                "criticidad": "alta"
            })
        
        # Validación 4: Verificar antigüedad de movimientos pendientes (ISO 9001 - Control de procesos)
        movimientos_antiguos = db.execute(text("""
            SELECT COUNT(*) as cantidad
            FROM stock 
            WHERE id_deposito = :id_deposito 
            AND codigo_art = :codigo_art
            AND (confirmado = 0 OR confirmado IS NULL)
            AND DATEDIFF(day, CAST(fecha AS DATE), GETDATE()) > 30
        """), {"id_deposito": id_deposito, "codigo_art": codigo_art}).scalar()
        
        if movimientos_antiguos > 0:
            warnings.append({
                "tipo": "movimientos_antiguos",
                "mensaje": f"{movimientos_antiguos} movimientos sin confirmar por más de 30 días",
                "criticidad": "media"
            })
        
        estado_validacion = "ok" if not inconsistencias else "error"
        if warnings and not inconsistencias:
            estado_validacion = "warning"
            
        return {
            "estado": estado_validacion,
            "stock_validado": stock_calculado,
            "inconsistencias": inconsistencias,
            "warnings": warnings,
            "fecha_validacion": datetime.now().isoformat(),
            "cumple_iso": len(inconsistencias) == 0
        }
        
    except Exception as e:
        logger.error(f"Error en validación de consistencia: {e}")
        return {
            "estado": "error",
            "mensaje": f"Error durante validación: {str(e)}",
            "fecha_validacion": datetime.now().isoformat(),
            "cumple_iso": False
        }

def calcular_stock_abc(db: Session, id_deposito: int = None) -> Dict[str, Any]:
    """
    Análisis ABC del stock según normas de gestión de inventarios ISO.
    Clasifica artículos por valor e importancia para optimización de recursos.
    
    Args:
        db: Sesión de base de datos
        id_deposito: ID del depósito (opcional, si no se especifica analiza todos)
        
    Returns:
        Diccionario con clasificación ABC de artículos
    """
    try:
        # Consulta base para obtener movimientos y calcular valores
        where_clause = "WHERE s.id_deposito = :id_deposito" if id_deposito else ""
        params = {"id_deposito": id_deposito} if id_deposito else {}
        
        query = text(f"""
            SELECT 
                s.codigo_art,
                a.descripcion,
                SUM(ABS(s.cant_disponible)) as total_movimientos,
                COUNT(DISTINCT s.nro_movimiento) as frecuencia_movimientos,
                AVG(s.cant_disponible) as promedio_stock
            FROM stock s
            LEFT JOIN articulos a ON s.codigo_art = a.id
            {where_clause}
            GROUP BY s.codigo_art, a.descripcion
            ORDER BY total_movimientos DESC
        """)
        
        resultados = db.execute(query, params).fetchall()
        
        if not resultados:
            return {"clasificacion": [], "total_articulos": 0}
        
        # Calcular percentiles para clasificación ABC
        total_articulos = len(resultados)
        limite_a = int(total_articulos * 0.2)  # 20% superior
        limite_b = int(total_articulos * 0.5)  # 30% medio (del 20% al 50%)
        
        clasificacion = []
        for idx, row in enumerate(resultados):
            if idx < limite_a:
                categoria = "A"
                prioridad = "Alta"
            elif idx < limite_b:
                categoria = "B" 
                prioridad = "Media"
            else:
                categoria = "C"
                prioridad = "Baja"
                
            clasificacion.append({
                "codigo_art": row.codigo_art,
                "descripcion": row.descripcion or "Sin descripción",
                "categoria_abc": categoria,
                "prioridad": prioridad,
                "total_movimientos": float(row.total_movimientos),
                "frecuencia_movimientos": row.frecuencia_movimientos,
                "promedio_stock": float(row.promedio_stock or 0)
            })
        
        return {
            "clasificacion": clasificacion,
            "total_articulos": total_articulos,
            "distribucion": {
                "categoria_a": limite_a,
                "categoria_b": limite_b - limite_a,
                "categoria_c": total_articulos - limite_b
            },
            "fecha_analisis": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en análisis ABC: {e}")
        return {"error": str(e)}