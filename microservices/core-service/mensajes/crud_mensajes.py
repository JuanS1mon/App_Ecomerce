from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime

from ...db.models.config.mensajes import Mensajes
from ...db.models.config.usuarios import Usuarios
from .schema_mensajes import MensajeCreate, MensajeUpdate, MensajeResponse, MensajeResumen, EstadisticasMensajes

class CrudMensajes:
    
    @staticmethod
    def crear_mensaje(db: Session, mensaje: MensajeCreate) -> Mensajes:
        """Crear un nuevo mensaje"""
        db_mensaje = Mensajes(
            usuario_emisor_id=mensaje.usuario_emisor_id,
            usuario_receptor_id=mensaje.usuario_receptor_id,
            titulo=mensaje.titulo,
            contenido=mensaje.contenido,
            tipo=mensaje.tipo,
            prioridad=mensaje.prioridad,
            metadatos=mensaje.metadatos
        )
        db.add(db_mensaje)
        db.commit()
        db.refresh(db_mensaje)
        return db_mensaje
    
    @staticmethod
    def obtener_mensaje(db: Session, mensaje_id: int) -> Optional[Mensajes]:
        """Obtener un mensaje por ID"""
        return db.query(Mensajes).filter(
            and_(Mensajes.id == mensaje_id, Mensajes.activo == True)
        ).first()
    
    @staticmethod
    def obtener_mensajes_usuario(
        db: Session, 
        usuario_id: int, 
        solo_no_leidos: bool = False,
        limite: int = 50,
        offset: int = 0
    ) -> List[MensajeResponse]:
        """Obtener mensajes de un usuario con información adicional"""
        query = db.query(
            Mensajes,
            Usuarios.nombre.label('nombre_emisor')
        ).outerjoin(
            Usuarios, Mensajes.usuario_emisor_id == Usuarios.codigo
        ).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        )
        
        if solo_no_leidos:
            query = query.filter(Mensajes.leido == False)
        
        query = query.order_by(desc(Mensajes.fecha_creacion))
        query = query.offset(offset).limit(limite)
        
        resultados = query.all()
        
        mensajes = []
        for mensaje, nombre_emisor in resultados:
            mensaje_response = MensajeResponse(
                id=mensaje.id,
                usuario_emisor_id=mensaje.usuario_emisor_id,
                usuario_receptor_id=mensaje.usuario_receptor_id,
                titulo=mensaje.titulo,
                contenido=mensaje.contenido,
                tipo=mensaje.tipo,
                prioridad=mensaje.prioridad,
                leido=mensaje.leido,
                fecha_creacion=mensaje.fecha_creacion,
                fecha_lectura=mensaje.fecha_lectura,
                activo=mensaje.activo,
                metadatos=mensaje.metadatos,
                nombre_emisor=nombre_emisor or "Sistema"
            )
            mensajes.append(mensaje_response)
        
        return mensajes
    
    @staticmethod
    def obtener_mensajes_recientes_navbar(db: Session, usuario_id: int, limite: int = 5) -> List[MensajeResumen]:
        """Obtener mensajes recientes para mostrar en la navbar"""
        query = db.query(
            Mensajes,
            Usuarios.nombre.label('nombre_emisor')
        ).outerjoin(
            Usuarios, Mensajes.usuario_emisor_id == Usuarios.codigo
        ).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).order_by(desc(Mensajes.fecha_creacion)).limit(limite)
        
        resultados = query.all()
        
        mensajes = []
        for mensaje, nombre_emisor in resultados:
            mensaje_resumen = MensajeResumen(
                id=mensaje.id,
                titulo=mensaje.titulo,
                tipo=mensaje.tipo,
                prioridad=mensaje.prioridad,
                leido=mensaje.leido,
                fecha_creacion=mensaje.fecha_creacion,
                nombre_emisor=nombre_emisor or "Sistema"
            )
            mensajes.append(mensaje_resumen)
        
        return mensajes
    
    @staticmethod
    def marcar_como_leido(db: Session, mensaje_id: int, usuario_id: int) -> bool:
        """Marcar un mensaje como leído"""
        mensaje = db.query(Mensajes).filter(
            and_(
                Mensajes.id == mensaje_id,
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).first()
        
        if mensaje and not mensaje.leido:
            mensaje.leido = True
            mensaje.fecha_lectura = datetime.now()
            db.commit()
            return True
        return False
    
    @staticmethod
    def marcar_todos_como_leidos(db: Session, usuario_id: int) -> int:
        """Marcar todos los mensajes de un usuario como leídos"""
        mensajes_actualizados = db.query(Mensajes).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.leido == False,
                Mensajes.activo == True
            )
        ).update({
            'leido': True,
            'fecha_lectura': datetime.now()
        })
        db.commit()
        return mensajes_actualizados
    
    @staticmethod
    def contar_mensajes_no_leidos(db: Session, usuario_id: int) -> int:
        """Contar mensajes no leídos de un usuario"""
        return db.query(Mensajes).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.leido == False,
                Mensajes.activo == True
            )
        ).count()
    
    @staticmethod
    def contar_todos_mensajes(db: Session, usuario_id: int) -> int:
        """Contar todos los mensajes de un usuario (leídos y no leídos)"""
        return db.query(Mensajes).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).count()
    
    @staticmethod
    def eliminar_mensaje(db: Session, mensaje_id: int, usuario_id: int) -> bool:
        """Eliminar (soft delete) un mensaje"""
        mensaje = db.query(Mensajes).filter(
            and_(
                Mensajes.id == mensaje_id,
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).first()
        
        if mensaje:
            mensaje.activo = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def obtener_estadisticas(db: Session, usuario_id: int) -> EstadisticasMensajes:
        """Obtener estadísticas de mensajes del usuario"""
        total_mensajes = db.query(Mensajes).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).count()
        
        mensajes_no_leidos = db.query(Mensajes).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.leido == False,
                Mensajes.activo == True
            )
        ).count()
        
        # Mensajes por tipo
        tipos = db.query(Mensajes.tipo, func.count(Mensajes.id)).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).group_by(Mensajes.tipo).all()
        
        mensajes_por_tipo = {tipo: count for tipo, count in tipos}
        
        # Mensajes por prioridad
        prioridades = db.query(Mensajes.prioridad, func.count(Mensajes.id)).filter(
            and_(
                Mensajes.usuario_receptor_id == usuario_id,
                Mensajes.activo == True
            )
        ).group_by(Mensajes.prioridad).all()
        
        mensajes_por_prioridad = {prioridad: count for prioridad, count in prioridades}
        
        return EstadisticasMensajes(
            total_mensajes=total_mensajes,
            mensajes_no_leidos=mensajes_no_leidos,
            mensajes_por_tipo=mensajes_por_tipo,
            mensajes_por_prioridad=mensajes_por_prioridad
        )
    
    # =============================
    # MÉTODOS PARA ADMINISTRACIÓN
    # =============================
    
    @staticmethod
    def get_mensajes_filtrados(db: Session, filtros: dict, skip: int = 0, limit: int = 50) -> List[MensajeResponse]:
        """Obtener mensajes con filtros para administración"""
        query = db.query(Mensajes)
        
        # Aplicar filtros
        if filtros.get('tipo'):
            query = query.filter(Mensajes.tipo == filtros['tipo'])
        if filtros.get('prioridad'):
            query = query.filter(Mensajes.prioridad == filtros['prioridad'])
        if filtros.get('leido') is not None:
            query = query.filter(Mensajes.leido == filtros['leido'])
        if filtros.get('usuario_id'):
            query = query.filter(Mensajes.usuario_receptor_id == filtros['usuario_id'])
        if filtros.get('fecha_desde'):
            query = query.filter(Mensajes.fecha_creacion >= filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            query = query.filter(Mensajes.fecha_creacion <= filtros['fecha_hasta'])
        if filtros.get('busqueda'):
            busqueda = f"%{filtros['busqueda']}%"
            query = query.filter(or_(
                Mensajes.titulo.ilike(busqueda),
                Mensajes.contenido.ilike(busqueda)
            ))
        
        mensajes = query.order_by(desc(Mensajes.fecha_creacion)).offset(skip).limit(limit).all()
        
        # Convertir a response con información adicional
        results = []
        for mensaje in mensajes:
            emisor = db.query(Usuarios).filter(Usuarios.codigo == mensaje.usuario_emisor_id).first() if mensaje.usuario_emisor_id else None
            receptor = db.query(Usuarios).filter(Usuarios.codigo == mensaje.usuario_receptor_id).first()
            
            results.append(MensajeResponse(
                id=mensaje.id,
                titulo=mensaje.titulo,
                contenido=mensaje.contenido,
                tipo=mensaje.tipo,
                prioridad=mensaje.prioridad,
                leido=mensaje.leido,
                fecha_creacion=mensaje.fecha_creacion,
                fecha_lectura=mensaje.fecha_lectura,
                metadatos=mensaje.metadatos,
                usuario_emisor_nombre=emisor.username if emisor else "Sistema",
                usuario_receptor_nombre=receptor.username if receptor else "Usuario Desconocido"
            ))
        
        return results
    
    @staticmethod
    def get_estadisticas_mensajes(db: Session) -> dict:
        """Obtener estadísticas generales de mensajes para administración"""
        total = db.query(func.count(Mensajes.id)).scalar()
        no_leidos = db.query(func.count(Mensajes.id)).filter(Mensajes.leido == False).scalar()
        urgentes = db.query(func.count(Mensajes.id)).filter(Mensajes.prioridad == 'alta').scalar()
        hoy = db.query(func.count(Mensajes.id)).filter(
            func.date(Mensajes.fecha_creacion) == datetime.now().date()
        ).scalar()
        
        # Estadísticas por tipo
        tipos_stats = db.query(
            Mensajes.tipo, 
            func.count(Mensajes.id)
        ).group_by(Mensajes.tipo).all()
        
        por_tipo = {tipo: count for tipo, count in tipos_stats}
        
        # Estadísticas por prioridad
        prioridad_stats = db.query(
            Mensajes.prioridad, 
            func.count(Mensajes.id)
        ).group_by(Mensajes.prioridad).all()
        
        por_prioridad = {prioridad: count for prioridad, count in prioridad_stats}
        
        return {
            "total": total,
            "no_leidos": no_leidos,
            "urgentes": urgentes,
            "hoy": hoy,
            "por_tipo": por_tipo,
            "por_prioridad": por_prioridad,
            "tendencia_semanal": []  # TODO: Implementar tendencia semanal
        }
    
    @staticmethod
    def verificar_usuario_existe(db: Session, usuario_id: int) -> bool:
        """Verificar si un usuario existe"""
        return db.query(Usuarios).filter(Usuarios.codigo == usuario_id).first() is not None
    
    @staticmethod
    def create_mensaje(db: Session, mensaje) -> Mensajes:
        """Crear mensaje (alias para compatibilidad)"""
        return CrudMensajes.crear_mensaje(db, mensaje)
    
    @staticmethod
    def get_mensaje_by_id(db: Session, mensaje_id: int) -> Optional[Mensajes]:
        """Obtener mensaje por ID (alias para compatibilidad)"""
        return CrudMensajes.obtener_mensaje(db, mensaje_id)
    
    @staticmethod
    def update_mensaje(db: Session, mensaje_id: int, mensaje_update) -> Optional[Mensajes]:
        """Actualizar un mensaje"""
        db_mensaje = db.query(Mensajes).filter(Mensajes.id == mensaje_id).first()
        if not db_mensaje:
            return None
        
        # Actualizar campos si se proporcionan
        if mensaje_update.titulo is not None:
            db_mensaje.titulo = mensaje_update.titulo
        if mensaje_update.contenido is not None:
            db_mensaje.contenido = mensaje_update.contenido
        if mensaje_update.tipo is not None:
            db_mensaje.tipo = mensaje_update.tipo
        if mensaje_update.prioridad is not None:
            db_mensaje.prioridad = mensaje_update.prioridad
        if mensaje_update.leido is not None:
            db_mensaje.leido = mensaje_update.leido
        if mensaje_update.metadatos is not None:
            db_mensaje.metadatos = mensaje_update.metadatos
        if mensaje_update.usuario_id is not None:
            db_mensaje.usuario_receptor_id = mensaje_update.usuario_id
        
        db.commit()
        db.refresh(db_mensaje)
        return db_mensaje
    
    @staticmethod
    def marcar_mensaje_leido(db: Session, mensaje_id: int, leido: bool) -> Optional[Mensajes]:
        """Cambiar estado de lectura de un mensaje"""
        db_mensaje = db.query(Mensajes).filter(Mensajes.id == mensaje_id).first()
        if not db_mensaje:
            return None
        
        db_mensaje.leido = leido
        if leido:
            db_mensaje.fecha_lectura = datetime.utcnow()
        else:
            db_mensaje.fecha_lectura = None
        
        db.commit()
        db.refresh(db_mensaje)
        return db_mensaje
    
    @staticmethod
    def delete_mensaje(db: Session, mensaje_id: int) -> bool:
        """Eliminar un mensaje"""
        db_mensaje = db.query(Mensajes).filter(Mensajes.id == mensaje_id).first()
        if not db_mensaje:
            return False
        
        db.delete(db_mensaje)
        db.commit()
        return True
    
    @staticmethod
    def get_usuarios_activos(db: Session) -> List[Usuarios]:
        """Obtener lista de usuarios activos"""
        return db.query(Usuarios).filter(Usuarios.activo == True).all()

    @staticmethod
    def get_mensajes_navbar(db: Session, usuario_id: int) -> dict:
        """Obtener mensajes para el navbar con información completa"""
        try:
            # Obtener mensajes del usuario
            mensajes_query = db.query(Mensajes).filter(
                and_(
                    Mensajes.usuario_receptor_id == usuario_id,
                    Mensajes.activo == True
                )
            ).order_by(desc(Mensajes.fecha_creacion)).limit(5)
            
            mensajes_db = mensajes_query.all()
            
            # Convertir a formato JSON serializable
            mensajes = []
            for mensaje in mensajes_db:
                mensajes.append({
                    "id": mensaje.id,
                    "titulo": mensaje.titulo,
                    "contenido": mensaje.contenido,
                    "tipo": mensaje.tipo,
                    "prioridad": mensaje.prioridad,
                    "leido": mensaje.leido,
                    "fecha_creacion": mensaje.fecha_creacion.isoformat() if mensaje.fecha_creacion else None,
                    "usuario_emisor_id": mensaje.usuario_emisor_id,
                    "usuario_receptor_id": mensaje.usuario_receptor_id,
                    "activo": mensaje.activo
                })
            
            return {
                "mensajes": mensajes,
                "total": len(mensajes),
                "usuario_id": usuario_id
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en get_mensajes_navbar: {e}")
            return {
                "mensajes": [],
                "total": 0,
                "usuario_id": usuario_id,
                "error": str(e)
            }
