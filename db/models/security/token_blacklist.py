# -*- coding: utf-8 -*-
"""
Modelo para tokens invalidados (blacklist)
Almacena tokens JWT que han sido revocados mediante logout
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from db.database import Base


class TokenBlacklist(Base):
    """
    Modelo para almacenar tokens JWT invalidados.
    
    Cuando un usuario hace logout, el token se agrega a esta tabla
    y se valida en cada petición para rechazar tokens revocados.
    
    Campos:
        - id: Identificador único
        - token: Token JWT completo (o su hash para mayor seguridad)
        - usuario_codigo: Código del usuario que hizo logout
        - razon: Razón de invalidación (logout, cambio_password, etc.)
        - fecha_invalidacion: Fecha y hora de invalidación
        - fecha_expiracion: Fecha de expiración original del token
    """
    __tablename__ = "token_blacklist"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)
    usuario_codigo = Column(Integer, nullable=True, index=True)
    razon = Column(String(100), nullable=False, default='logout')  # logout, password_change, admin_revoke
    fecha_invalidacion = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    def __repr__(self):
        return f"<TokenBlacklist(id={self.id}, usuario_codigo={self.usuario_codigo}, razon='{self.razon}')>"
    
    @classmethod
    def is_token_blacklisted(cls, db, token: str) -> bool:
        """
        Verifica si un token está en la lista negra.
        
        Args:
            db: Sesión de base de datos
            token: Token JWT a verificar
            
        Returns:
            bool: True si el token está en la lista negra, False si no
        """
        result = db.query(cls).filter(cls.token == token).first()
        return result is not None
    
    @classmethod
    def add_to_blacklist(cls, db, token: str, usuario_codigo: int, 
                         fecha_expiracion, razon: str = 'logout',
                         user_agent: str = None, ip_address: str = None):
        """
        Agrega un token a la lista negra.
        
        Args:
            db: Sesión de base de datos
            token: Token JWT a invalidar
            usuario_codigo: Código del usuario
            fecha_expiracion: Fecha de expiración del token
            razon: Razón de invalidación
            user_agent: User agent del cliente
            ip_address: Dirección IP del cliente
        """
        blacklist_entry = cls(
            token=token,
            usuario_codigo=usuario_codigo,
            razon=razon,
            fecha_expiracion=fecha_expiracion,
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.add(blacklist_entry)
        db.commit()
        return blacklist_entry
    
    @classmethod
    def cleanup_expired_tokens(cls, db):
        """
        Elimina tokens que ya expiraron de la lista negra.
        Debe ejecutarse periódicamente (ej: cada hora o diariamente).
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            int: Cantidad de tokens eliminados
        """
        from datetime import datetime, timezone
        
        deleted_count = db.query(cls).filter(
            cls.fecha_expiracion < datetime.now(timezone.utc)
        ).delete()
        db.commit()
        return deleted_count
    
    @classmethod
    def revoke_all_user_tokens(cls, db, usuario_codigo: int, razon: str = 'admin_revoke'):
        """
        Invalida todos los tokens de un usuario específico.
        Útil para forzar logout en caso de cambio de password o acción administrativa.
        
        Args:
            db: Sesión de base de datos
            usuario_codigo: Código del usuario
            razon: Razón de invalidación
            
        Returns:
            int: Cantidad de tokens revocados
        """
        # Nota: Esto requeriría almacenar todos los tokens activos,
        # por ahora solo marcamos la acción
        # En producción, podrías implementar un sistema más sofisticado
        pass
