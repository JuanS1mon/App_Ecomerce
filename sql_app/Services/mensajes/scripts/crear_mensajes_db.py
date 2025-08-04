#!/usr/bin/env python3
"""
Script para crear mensajes de prueba directamente en la base de datos
Ubicado en: sql_app/Services/mensajes/scripts/crear_mensajes_db.py
"""

import sys
import os

# Ajustar el path para importar desde la raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))  # /Services/mensajes/scripts/
services_dir = os.path.dirname(script_dir)  # /Services/mensajes/
sql_app_dir = os.path.dirname(os.path.dirname(services_dir))  # /sql_app/
project_root = os.path.dirname(sql_app_dir)  # raíz del proyecto

sys.path.insert(0, project_root)

from sqlalchemy.orm import Session
from sql_app.db.database import get_db, engine
from sql_app.db.models.config.mensajes import Mensajes
from sql_app.db.models.config.usuarios import Usuarios
from datetime import datetime
import json

def crear_mensajes_prueba():
    """Crear mensajes de prueba en la base de datos"""
    print("📨 CREANDO MENSAJES DE PRUEBA")
    print("=" * 40)
    
    # Crear sesión de base de datos
    db = Session(engine)
    
    try:
        # Obtener usuarios existentes
        usuarios = db.query(Usuarios).all()
        print(f"👥 Usuarios disponibles: {len(usuarios)}")
        
        if not usuarios:
            print("❌ No hay usuarios en la base de datos")
            return
        
        for usuario in usuarios[:3]:
            print(f"   - {usuario.codigo}: {usuario.usuario} ({usuario.mail})")
        
        # Crear mensajes de ejemplo
        mensajes_ejemplo = [
            {
                "titulo": "¡Bienvenido al Sistema!",
                "contenido": "Este es tu primer mensaje en el sistema de administración. Aquí podrás gestionar todas las notificaciones y comunicaciones importantes.",
                "tipo": "sistema",
                "prioridad": "normal",
                "usuario_id": usuarios[0].codigo,
                "leido": False,
                "metadatos": {"origen": "sistema", "categoria": "bienvenida"}
            },
            {
                "titulo": "Mantenimiento Programado",
                "contenido": "El sistema estará en mantenimiento el próximo domingo de 2:00 AM a 6:00 AM. Durante este tiempo, algunas funcionalidades podrían no estar disponibles.",
                "tipo": "alerta",
                "prioridad": "alta",
                "usuario_id": usuarios[0].codigo,
                "leido": False,
                "metadatos": {"origen": "admin", "fecha_mantenimiento": "2025-01-28"}
            },
            {
                "titulo": "Nueva Función: Reportes Avanzados",
                "contenido": "Ya está disponible la nueva función de reportes avanzados en el menú de análisis. Podrás generar reportes personalizados y exportarlos en múltiples formatos.",
                "tipo": "notificacion",
                "prioridad": "normal",
                "usuario_id": usuarios[0].codigo,
                "leido": True,
                "metadatos": {"origen": "producto", "version": "2.1.0"}
            },
            {
                "titulo": "Recordatorio: Actualizar Perfil",
                "contenido": "Recuerda actualizar tu información de perfil para mantener tus datos actualizados en el sistema.",
                "tipo": "usuario",
                "prioridad": "baja",
                "usuario_id": usuarios[0].codigo,
                "leido": False,
                "metadatos": {"origen": "sistema", "tipo_recordatorio": "perfil"}
            },
            {
                "titulo": "¡Felicidades! Nuevo Logro Desbloqueado",
                "contenido": "Has desbloqueado el logro 'Explorador' por navegar por todas las secciones del sistema. ¡Sigue explorando para desbloquear más logros!",
                "tipo": "notificacion",
                "prioridad": "baja",
                "usuario_id": usuarios[0].codigo,
                "leido": True,
                "metadatos": {"origen": "gamificacion", "logro": "explorador"}
            },
            {
                "titulo": "🚨 URGENTE: Actualización de Seguridad",
                "contenido": "Se ha detectado una vulnerabilidad de seguridad. Por favor, cambia tu contraseña inmediatamente y revisa tu actividad reciente.",
                "tipo": "alerta",
                "prioridad": "urgente",
                "usuario_id": usuarios[0].codigo,
                "leido": False,
                "metadatos": {"origen": "seguridad", "nivel_alerta": "critico"}
            }
        ]
        
        # Si hay más usuarios, distribuir mensajes
        if len(usuarios) > 1:
            mensajes_ejemplo.extend([
                {
                    "titulo": "Invitación a Colaborar",
                    "contenido": f"Te han invitado a colaborar en el proyecto 'Sistema de Gestión'. Revisa los detalles en tu panel de proyectos.",
                    "tipo": "usuario",
                    "prioridad": "normal",
                    "usuario_id": usuarios[1].codigo,
                    "leido": False,
                    "metadatos": {"origen": "colaboracion", "proyecto_id": "12345"}
                },
                {
                    "titulo": "Backup Completado",
                    "contenido": "El backup automático del sistema se ha completado exitosamente. Todos tus datos están seguros.",
                    "tipo": "sistema",
                    "prioridad": "normal", 
                    "usuario_id": usuarios[1].codigo,
                    "leido": True,
                    "metadatos": {"origen": "backup", "backup_id": "backup_20250121"}
                }
            ])
        
        # Insertar mensajes
        mensajes_creados = 0
        for mensaje_data in mensajes_ejemplo:
            try:
                # Verificar si ya existe un mensaje similar
                existe = db.query(Mensajes).filter(Mensajes.titulo == mensaje_data["titulo"]).first()
                
                if not existe:
                    nuevo_mensaje = Mensajes(
                        titulo=mensaje_data["titulo"],
                        contenido=mensaje_data["contenido"],
                        tipo=mensaje_data["tipo"],
                        prioridad=mensaje_data["prioridad"],
                        usuario_receptor_id=mensaje_data["usuario_id"],
                        leido=mensaje_data["leido"],
                        fecha_creacion=datetime.utcnow(),
                        fecha_lectura=datetime.utcnow() if mensaje_data["leido"] else None,
                        metadatos=json.dumps(mensaje_data["metadatos"]),
                        activo=True
                    )
                    
                    db.add(nuevo_mensaje)
                    mensajes_creados += 1
                    print(f"✅ Creado: {mensaje_data['titulo'][:50]}...")
                else:
                    print(f"⏭️  Ya existe: {mensaje_data['titulo'][:50]}...")
                    
            except Exception as e:
                print(f"❌ Error creando mensaje: {e}")
        
        db.commit()
        
        # Mostrar resumen
        total_mensajes = db.query(Mensajes).count()
        no_leidos = db.query(Mensajes).filter(Mensajes.leido == False).count()
        urgentes = db.query(Mensajes).filter(Mensajes.prioridad == "urgente").count()
        
        print(f"\n📊 RESUMEN:")
        print(f"   Mensajes creados: {mensajes_creados}")
        print(f"   Total en BD: {total_mensajes}")
        print(f"   No leídos: {no_leidos}")
        print(f"   Urgentes: {urgentes}")
        
        print(f"\n🎯 PÁGINA LISTA PARA PROBAR:")
        print(f"   http://localhost:8000/static/admin/mensajes.html")
        print(f"   🔑 Los datos están en la base de datos y listos para mostrar")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    crear_mensajes_prueba()
