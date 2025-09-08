# =============================
# SISTEMA DE NOTIFICACIONES
# =============================
# Sistema para enviar alertas por email, Slack, etc.

import smtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import json
import aiohttp
from sql_app.config import ENVIRONMENT
import os

logger = logging.getLogger("notifications")

class NotificationManager:
    """Gestor de notificaciones para alertas del sistema"""
    
    def __init__(self):
        self.email_config = {
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("NOTIFICATION_EMAIL"),
            "password": os.getenv("NOTIFICATION_EMAIL_PASSWORD"),
            "from_email": os.getenv("NOTIFICATION_FROM_EMAIL")
        }
        
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
        
        # Solo enviar notificaciones en producción por defecto
        self.enabled = ENVIRONMENT == "production" or os.getenv("NOTIFICATIONS_ENABLED", "false").lower() == "true"
        
        if self.enabled:
            logger.info("🔔 Sistema de notificaciones habilitado")
        else:
            logger.info("🔕 Sistema de notificaciones deshabilitado (desarrollo)")
    
    async def send_alert(self, alert_data: Dict):
        """Envía una alerta por múltiples canales"""
        if not self.enabled:
            logger.info(f"🔕 Alerta omitida (dev): {alert_data.get('summary', 'Sin título')}")
            return
        
        try:
            severity = alert_data.get('severity', 'info')
            
            # Log de la alerta
            logger.warning(f"🚨 ALERTA [{severity.upper()}]: {alert_data.get('summary')}")
            
            # Enviar por email para alertas críticas
            if severity in ['critical', 'warning'] and self.email_config["username"]:
                await self._send_email_alert(alert_data)
            
            # Enviar por Slack si está configurado
            if self.slack_webhook:
                await self._send_slack_alert(alert_data)
                
        except Exception as e:
            logger.error(f"❌ Error enviando alerta: {e}")
    
    async def _send_email_alert(self, alert_data: Dict):
        """Envía alerta por email"""
        try:
            if not self.admin_emails or not self.email_config["username"]:
                return
            
            # Preparar mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_config["from_email"] or self.email_config["username"]
            msg['To'] = ", ".join([email.strip() for email in self.admin_emails if email.strip()])
            
            severity = alert_data.get('severity', 'info')
            summary = alert_data.get('summary', 'Alerta del sistema')
            
            # Emoji según severidad
            emoji = {
                'critical': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(severity, '📢')
            
            msg['Subject'] = f"{emoji} [{severity.upper()}] Stock Management Alert"
            
            # Cuerpo del email
            body = f"""
            <html>
            <body>
                <h2>{emoji} Alerta del Sistema de Stock Management</h2>
                
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <td><strong>Severidad</strong></td>
                        <td style="color: {'red' if severity == 'critical' else 'orange' if severity == 'warning' else 'blue'};">
                            {severity.upper()}
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Resumen</strong></td>
                        <td>{summary}</td>
                    </tr>
                    <tr>
                        <td><strong>Descripción</strong></td>
                        <td>{alert_data.get('description', 'Sin descripción')}</td>
                    </tr>
                    <tr>
                        <td><strong>Servicio</strong></td>
                        <td>{alert_data.get('service', 'Sistema')}</td>
                    </tr>
                    <tr>
                        <td><strong>Timestamp</strong></td>
                        <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td><strong>Ambiente</strong></td>
                        <td>{ENVIRONMENT}</td>
                    </tr>
                </table>
                
                <br>
                <p><strong>Acciones recomendadas:</strong></p>
                <ul>
                    <li>Revisar logs de la aplicación</li>
                    <li>Verificar métricas en Grafana: <a href="http://localhost:3000">Dashboard</a></li>
                    <li>Comprobar estado del sistema: <a href="http://localhost:8000/health">Health Check</a></li>
                </ul>
                
                <hr>
                <small>Este mensaje fue generado automáticamente por el sistema de monitoreo.</small>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email (en hilo separado para no bloquear)
            await asyncio.get_event_loop().run_in_executor(
                None, self._send_smtp_email, msg
            )
            
            logger.info(f"📧 Email de alerta enviado a {len(self.admin_emails)} destinatarios")
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
    
    def _send_smtp_email(self, msg):
        """Envía email usando SMTP (función sincrónica)"""
        try:
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            text = msg.as_string()
            server.sendmail(msg['From'], msg['To'].split(", "), text)
            server.quit()
        except Exception as e:
            logger.error(f"❌ Error SMTP: {e}")
            raise
    
    async def _send_slack_alert(self, alert_data: Dict):
        """Envía alerta a Slack"""
        try:
            severity = alert_data.get('severity', 'info')
            
            # Color según severidad
            colors = {
                'critical': '#FF0000',  # Rojo
                'warning': '#FFA500',   # Naranja
                'info': '#0000FF'       # Azul
            }
            
            # Emoji según severidad
            emoji = {
                'critical': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(severity, '📢')
            
            payload = {
                "username": "Stock Management Monitor",
                "icon_emoji": ":robot_face:",
                "attachments": [
                    {
                        "color": colors.get(severity, '#0000FF'),
                        "title": f"{emoji} {alert_data.get('summary', 'Alerta del sistema')}",
                        "text": alert_data.get('description', 'Sin descripción'),
                        "fields": [
                            {
                                "title": "Severidad",
                                "value": severity.upper(),
                                "short": True
                            },
                            {
                                "title": "Servicio",
                                "value": alert_data.get('service', 'Sistema'),
                                "short": True
                            },
                            {
                                "title": "Ambiente",
                                "value": ENVIRONMENT,
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            }
                        ],
                        "footer": "Stock Management Monitor",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info("💬 Alerta enviada a Slack")
                    else:
                        logger.error(f"❌ Error enviando a Slack: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Error enviando a Slack: {e}")
    
    async def send_system_status(self, status_data: Dict):
        """Envía reporte de estado del sistema"""
        if not self.enabled:
            return
        
        try:
            # Solo enviar si hay algo importante que reportar
            if status_data.get('requires_attention', False):
                await self.send_alert({
                    'severity': 'info',
                    'summary': 'Reporte de estado del sistema',
                    'description': f"Estado: {status_data.get('status', 'unknown')}",
                    'service': 'system-monitor'
                })
        except Exception as e:
            logger.error(f"❌ Error enviando reporte de estado: {e}")
    
    async def test_notifications(self):
        """Prueba el sistema de notificaciones"""
        test_alert = {
            'severity': 'info',
            'summary': 'Prueba del sistema de notificaciones',
            'description': 'Este es un mensaje de prueba para verificar que las notificaciones funcionan correctamente.',
            'service': 'notification-test'
        }
        
        await self.send_alert(test_alert)
        logger.info("✅ Prueba de notificaciones completada")

# =============================
# INSTANCIA GLOBAL
# =============================
notification_manager = NotificationManager()

# =============================
# FUNCIONES DE UTILIDAD
# =============================

async def send_alert(severity: str, summary: str, description: str = "", service: str = "system"):
    """Función helper para enviar alertas"""
    await notification_manager.send_alert({
        'severity': severity,
        'summary': summary,
        'description': description,
        'service': service
    })

async def send_critical_alert(summary: str, description: str = "", service: str = "system"):
    """Envía alerta crítica"""
    await send_alert('critical', summary, description, service)

async def send_warning_alert(summary: str, description: str = "", service: str = "system"):
    """Envía alerta de warning"""
    await send_alert('warning', summary, description, service)

async def send_info_alert(summary: str, description: str = "", service: str = "system"):
    """Envía alerta informativa"""
    await send_alert('info', summary, description, service)
