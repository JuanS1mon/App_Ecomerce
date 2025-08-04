# 🐳 Docker Setup - Sistema de Gestión de Stock

Este proyecto está configurado para ejecutarse con **Docker** usando dos contenedores separados:
- **FastAPI Application** (Puerto 8000)
- **Microsoft SQL Server** (Puerto 1433)

## 📋 Requisitos

- Docker Desktop
- Docker Compose
- 4GB RAM disponible (mínimo)
- 10GB espacio en disco

## 🚀 Inicio Rápido

### Para Desarrollo

```bash
# Usando el script automático (Windows)
start-dev.bat

# O manualmente
docker-compose -f docker-compose.dev.yml up --build -d
```

### Para Producción

```bash
# Usando el script automático (Windows)
start-prod.bat

# O manualmente
docker-compose up --build -d
```

## 🛠️ Servicios Incluidos

### 1. Base de Datos (SQL Server)
- **Imagen:** `mcr.microsoft.com/mssql/server:2022-latest`
- **Puerto:** 1433
- **Usuario:** sa
- **Contraseña:** 
  - Desarrollo: `DevPassword123!`
  - Producción: `MyStrongPassword123!`

### 2. Aplicación FastAPI
- **Puerto:** 8000
- **Auto-reload:** Habilitado en desarrollo
- **Workers:** 1 en desarrollo, 4 en producción

### 3. Nginx (Solo Producción)
- **Puerto:** 80 (HTTP), 443 (HTTPS)
- **Proxy reverso** hacia FastAPI

## 📁 Estructura de Archivos Docker

```
sql_app/
├── Dockerfile                    # Imagen de la aplicación
├── docker-compose.yml          # Configuración de producción
├── docker-compose.dev.yml      # Configuración de desarrollo
├── docker-entrypoint.sh        # Script de inicialización
├── .dockerignore               # Archivos excluidos del build
├── .env.docker                 # Variables de entorno
├── database/
│   └── init/
│       └── 01-init.sql         # Script de inicialización DB
├── start-dev.bat              # Script de inicio desarrollo
├── start-prod.bat             # Script de inicio producción
└── stop-services.bat          # Script para detener servicios
```

## 🔧 Comandos Útiles

### Gestión de Contenedores

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f app
docker-compose logs -f database

# Reiniciar un servicio
docker-compose restart app

# Entrar al contenedor de la aplicación
docker-compose exec app bash

# Entrar al contenedor de la base de datos
docker-compose exec database /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "MyStrongPassword123!"
```

### Base de Datos

```bash
# Ejecutar migración manual
docker-compose exec app alembic upgrade head

# Crear nueva migración
docker-compose exec app alembic revision --autogenerate -m "Descripción"

# Backup de base de datos
docker-compose exec database /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "MyStrongPassword123!" -Q "BACKUP DATABASE StockApp TO DISK = '/var/opt/mssql/backup/stockapp.bak'"
```

### Desarrollo

```bash
# Rebuild solo la aplicación
docker-compose build app

# Reiniciar con rebuild
docker-compose up --build -d

# Ver estado de servicios
docker-compose ps
```

## 🌍 Variables de Entorno

### Principales Variables

| Variable | Desarrollo | Producción | Descripción |
|----------|------------|------------|-------------|
| `DATABASE_URL` | Auto | Auto | Cadena de conexión completa |
| `ENVIRONMENT` | development | production | Entorno de ejecución |
| `SECRET_KEY` | dev-key | **CAMBIAR** | Clave secreta JWT |
| `LOG_LEVEL` | DEBUG | INFO | Nivel de logging |

### Personalización

Copia `.env.docker` a `.env.local` y modifica según necesites:

```bash
cp .env.docker .env.local
# Editar .env.local con tus configuraciones
```

## 📊 Monitoreo y Logs

### Ubicaciones de Logs

- **Aplicación:** `/app/logs/` (montado en `./logs/`)
- **Base de datos:** Logs internos de SQL Server
- **Nginx:** Logs estándar de Nginx

### Health Checks

Todos los servicios incluyen health checks:

```bash
# Verificar estado de salud
curl http://localhost:8000/health
```

## 🔒 Seguridad

### Producción

1. **Cambiar contraseñas por defecto**
2. **Configurar SSL/TLS**
3. **Usar usuario de BD específico (no sa)**
4. **Configurar firewall**
5. **Backup regular**

### Configuración SSL (Opcional)

```bash
# Generar certificados auto-firmados para testing
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **Puerto 1433 en uso**
   ```bash
   # Cambiar puerto en docker-compose.yml
   ports:
     - "1434:1433"  # Usar puerto 1434 localmente
   ```

2. **Memoria insuficiente**
   ```bash
   # Reducir memoria de SQL Server
   environment:
     MSSQL_MEMORY_LIMIT_MB: 1024
   ```

3. **Aplicación no conecta a BD**
   ```bash
   # Verificar logs
   docker-compose logs database
   docker-compose logs app
   ```

### Limpieza Completa

```bash
# Detener y limpiar todo
docker-compose down -v
docker system prune -af
docker volume prune -f
```

## 📈 Escalabilidad

### Múltiples Instancias de App

```yaml
# En docker-compose.yml
app:
  deploy:
    replicas: 3
  # ... resto de configuración
```

### Load Balancer

Nginx ya está configurado como load balancer para múltiples instancias.

## 🔄 Backup y Restore

### Script de Backup Automático

```bash
# Backup diario (agregar a cron)
docker-compose exec -T database /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P "MyStrongPassword123!" \
  -Q "BACKUP DATABASE StockApp TO DISK = '/var/opt/mssql/backup/stockapp_$(date +%Y%m%d).bak'"
```

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs: `docker-compose logs -f`
2. Verificar documentación de la aplicación
3. Contactar al equipo de desarrollo

---

✨ **¡Tu aplicación está lista para ejecutarse con Docker!**
