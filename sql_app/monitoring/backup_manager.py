# =============================
# SISTEMA DE BACKUP AUTOMÁTICO
# =============================
# Sistema para backup automático de base de datos y configuraciones

import os
import asyncio
import logging
import subprocess
import shutil
import zipfile
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import json

from sql_app.config import ENVIRONMENT
from sql_app.monitoring.notifications import notification_manager

logger = logging.getLogger("backup_manager")

class BackupManager:
    """Gestor de backups automáticos"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuración de backup
        self.config = {
            'db_enabled': os.getenv('BACKUP_DB_ENABLED', 'true').lower() == 'true',
            'files_enabled': os.getenv('BACKUP_FILES_ENABLED', 'true').lower() == 'true',
            'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
            'daily_time': os.getenv('BACKUP_DAILY_TIME', '02:00'),  # 2 AM
            'weekly_day': os.getenv('BACKUP_WEEKLY_DAY', 'sunday'),
            'compress': os.getenv('BACKUP_COMPRESS', 'true').lower() == 'true'
        }
        
        # Solo en producción por defecto
        self.enabled = ENVIRONMENT == "production" or os.getenv('BACKUP_ENABLED', 'false').lower() == 'true'
        
        if self.enabled:
            logger.info("💾 Sistema de backup habilitado")
            self._schedule_backups()
        else:
            logger.info("💾 Sistema de backup deshabilitado (desarrollo)")
    
    def _schedule_backups(self):
        """Programa los backups automáticos"""
        try:
            # Backup diario de BD
            if self.config['db_enabled']:
                schedule.every().day.at(self.config['daily_time']).do(
                    self._run_async_backup, 'database'
                )
                logger.info(f"📅 Backup de BD programado diariamente a las {self.config['daily_time']}")
            
            # Backup semanal de archivos
            if self.config['files_enabled']:
                getattr(schedule.every(), self.config['weekly_day']).at(self.config['daily_time']).do(
                    self._run_async_backup, 'files'
                )
                logger.info(f"📅 Backup de archivos programado {self.config['weekly_day']}s a las {self.config['daily_time']}")
            
            # Limpieza de backups antiguos (diario)
            schedule.every().day.at("03:00").do(self._run_async_cleanup)
            
        except Exception as e:
            logger.error(f"❌ Error programando backups: {e}")
    
    def _run_async_backup(self, backup_type: str):
        """Ejecuta backup de forma asíncrona"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if backup_type == 'database':
                loop.run_until_complete(self.backup_database())
            elif backup_type == 'files':
                loop.run_until_complete(self.backup_files())
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando backup {backup_type}: {e}")
        finally:
            loop.close()
    
    def _run_async_cleanup(self):
        """Ejecuta limpieza de forma asíncrona"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.cleanup_old_backups())
        except Exception as e:
            logger.error(f"❌ Error en limpieza de backups: {e}")
        finally:
            loop.close()
    
    async def backup_database(self) -> Optional[str]:
        """Realiza backup de la base de datos"""
        if not self.enabled or not self.config['db_enabled']:
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"db_backup_{timestamp}"
            backup_path = self.backup_dir / f"{backup_name}.sql"
            
            logger.info(f"💾 Iniciando backup de BD: {backup_name}")
            
            # Obtener configuración de BD
            db_server = os.getenv('DB_HOST', 'localhost')
            db_name = os.getenv('DB_NAME', 'sql_app')
            db_user = os.getenv('DB_USER', 'sa')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Comando sqlcmd para backup
            cmd = [
                'sqlcmd',
                '-S', db_server,
                '-d', db_name,
                '-U', db_user,
                '-P', db_password,
                '-Q', f"BACKUP DATABASE [{db_name}] TO DISK = '{backup_path}' WITH FORMAT, INIT"
            ]
            
            # Ejecutar backup
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Comprimir si está habilitado
                final_path = backup_path
                if self.config['compress']:
                    final_path = await self._compress_file(backup_path)
                    backup_path.unlink()  # Eliminar archivo sin comprimir
                
                file_size = final_path.stat().st_size / (1024 * 1024)  # MB
                
                await notification_manager.send_alert({
                    'severity': 'info',
                    'summary': 'Backup de BD completado',
                    'description': f'Backup guardado: {final_path.name} ({file_size:.1f} MB)',
                    'service': 'backup-manager'
                })
                
                logger.info(f"✅ Backup de BD completado: {final_path.name} ({file_size:.1f} MB)")
                return str(final_path)
                
            else:
                error_msg = stderr.decode() if stderr else "Error desconocido"
                logger.error(f"❌ Error en backup de BD: {error_msg}")
                
                await notification_manager.send_alert({
                    'severity': 'critical',
                    'summary': 'Error en backup de BD',
                    'description': f'Error: {error_msg}',
                    'service': 'backup-manager'
                })
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción en backup de BD: {e}")
            
            await notification_manager.send_alert({
                'severity': 'critical',
                'summary': 'Fallo en backup de BD',
                'description': f'Excepción: {str(e)}',
                'service': 'backup-manager'
            })
            
            return None
    
    async def backup_files(self) -> Optional[str]:
        """Realiza backup de archivos importantes"""
        if not self.enabled or not self.config['files_enabled']:
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"files_backup_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            logger.info(f"📁 Iniciando backup de archivos: {backup_name}")
            
            # Archivos y carpetas a respaldar
            items_to_backup = [
                'sql_app/static',
                'logs',
                '.env.production.example',
                'docker-compose.production-v2.yml',
                'Dockerfile',
                'requirements.txt',
                'monitoring',
                'nginx.conf'
            ]
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for item in items_to_backup:
                    item_path = Path(item)
                    if item_path.exists():
                        if item_path.is_file():
                            zipf.write(item_path, item_path.name)
                        elif item_path.is_dir():
                            for file_path in item_path.rglob('*'):
                                if file_path.is_file():
                                    arcname = file_path.relative_to(item_path.parent)
                                    zipf.write(file_path, arcname)
            
            file_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            
            await notification_manager.send_alert({
                'severity': 'info',
                'summary': 'Backup de archivos completado',
                'description': f'Backup guardado: {backup_name} ({file_size:.1f} MB)',
                'service': 'backup-manager'
            })
            
            logger.info(f"✅ Backup de archivos completado: {backup_name} ({file_size:.1f} MB)")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Error en backup de archivos: {e}")
            
            await notification_manager.send_alert({
                'severity': 'warning',
                'summary': 'Error en backup de archivos',
                'description': f'Error: {str(e)}',
                'service': 'backup-manager'
            })
            
            return None
    
    async def _compress_file(self, file_path: Path) -> Path:
        """Comprime un archivo usando gzip"""
        import gzip
        
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    async def cleanup_old_backups(self):
        """Limpia backups antiguos según la política de retención"""
        if not self.enabled:
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
            deleted_count = 0
            
            for backup_file in self.backup_dir.iterdir():
                if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"🗑️ Backup eliminado: {backup_file.name}")
            
            if deleted_count > 0:
                logger.info(f"🧹 Limpieza completada: {deleted_count} backups eliminados")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de backups: {e}")
    
    async def list_backups(self) -> List[Dict]:
        """Lista todos los backups disponibles"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if backup_file.is_file():
                stat = backup_file.stat()
                backups.append({
                    'name': backup_file.name,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': 'database' if 'db_backup' in backup_file.name else 'files'
                })
        
        return backups
    
    async def restore_database(self, backup_file: str) -> bool:
        """Restaura la base de datos desde un backup"""
        # IMPLEMENTAR SOLO SI ES NECESARIO Y CON MUCHO CUIDADO
        logger.warning("⚠️ Restauración de BD no implementada por seguridad")
        return False
    
    def start_scheduler(self):
        """Inicia el scheduler de backups"""
        if not self.enabled:
            return
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        
        import threading
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("⏰ Scheduler de backups iniciado")

# =============================
# INSTANCIA GLOBAL
# =============================
backup_manager = BackupManager()

# =============================
# FUNCIONES DE UTILIDAD
# =============================

async def manual_backup() -> Dict[str, str]:
    """Ejecuta backup manual"""
    results = {}
    
    if backup_manager.config['db_enabled']:
        db_backup = await backup_manager.backup_database()
        results['database'] = db_backup or "Failed"
    
    if backup_manager.config['files_enabled']:
        files_backup = await backup_manager.backup_files()
        results['files'] = files_backup or "Failed"
    
    return results

def init_backup_system():
    """Inicializa el sistema de backup"""
    backup_manager.start_scheduler()
    logger.info("💾 Sistema de backup inicializado")
