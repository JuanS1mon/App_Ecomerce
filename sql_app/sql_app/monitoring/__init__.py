# Monitoring package initialization
from .metrics import (
    MetricsMiddleware,
    metrics_endpoint,
    record_cache_operation,
    record_auth_attempt,
    record_rate_limit_hit,
    record_db_query,
    update_db_connections,
    track_db_query,
    track_cache_operation,
    init_metrics
)

# Phase 3: Advanced monitoring
from .health_checks import (
    health_checker,
    init_health_checks,
    get_health_status
)

from .notifications import (
    notification_manager,
    send_alert,
    send_critical_alert,
    send_warning_alert,
    send_info_alert
)

from .backup_manager import (
    backup_manager,
    manual_backup,
    init_backup_system
)

__all__ = [
    # Metrics
    "MetricsMiddleware",
    "metrics_endpoint",
    "record_cache_operation",
    "record_auth_attempt",
    "record_rate_limit_hit",
    "record_db_query",
    "update_db_connections",
    "track_db_query",
    "track_cache_operation",
    "init_metrics",
    
    # Health checks
    "health_checker",
    "init_health_checks",
    "get_health_status",
    
    # Notifications
    "notification_manager",
    "send_alert",
    "send_critical_alert",
    "send_warning_alert",
    "send_info_alert",
    
    # Backup
    "backup_manager",
    "manual_backup",
    "init_backup_system"
]
