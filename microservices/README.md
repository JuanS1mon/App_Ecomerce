# 🏗️ ARQUITECTURA DE MICROSERVICIOS

## 📋 **RESUMEN EJECUTIVO**

Este proyecto ha sido migrado de una arquitectura monolítica a una arquitectura de microservicios para mejorar la escalabilidad, mantenibilidad y capacidad de despliegue independiente de cada componente del sistema.

## 🎯 **OBJETIVOS DE LA SEPARACIÓN**

### **Servicios CORE separados:**
- ✅ **admin** - Panel de administración general
- ✅ **security** - Autenticación, JWT, roles, middleware
- ✅ **mail** - Sistema de correos electrónicos
- ✅ **chat** - Sistema de comunicación en tiempo real
- ✅ **mensajes** - Sistema de mensajes/notificaciones

### **Servicios de Aplicación independientes:**
- ✅ **app_stock** - Gestión de inventario y stock
- ✅ **app_obras** - Gestión de obras y proyectos
- 🔄 **tickets** - Sistema de soporte (pendiente)
- 🔄 **widgets** - Componentes reutilizables (pendiente)

## 🏗️ **ARQUITECTURA**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API GATEWAY   │    │   MONITORING    │    │    DATABASE     │
│     (NGINX)     │    │ (Prometheus +   │    │   (SQL Server)  │
│   Port: 80      │    │    Grafana)     │    │   Port: 1433    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
    ┌─────────────┬───────────────┼───────────────┬─────────────┐
    │             │               │               │             │
┌───▼────┐ ┌─────▼────┐ ┌────────▼────────┐ ┌───▼────┐ ┌─────▼────┐
│ CORE   │ │  STOCK   │ │      OBRAS      │ │  ...   │ │   ...    │
│SERVICE │ │ SERVICE  │ │    SERVICE      │ │SERVICE │ │ SERVICE  │
│Port:   │ │ Port:    │ │     Port:       │ │        │ │          │
│ 8001   │ │  8002    │ │      8003       │ │        │ │          │
└────────┘ └──────────┘ └─────────────────┘ └────────┘ └──────────┘
```

## 🚀 **INICIO RÁPIDO**

### **Prerrequisitos:**
- Docker Desktop instalado
- Docker Compose habilitado
- Al menos 4GB de RAM disponible

### **1. Clonar y navegar:**
```bash
cd microservices
```

### **2. Iniciar servicios:**

**En Windows:**
```cmd
start-microservices.bat
```

**En Linux/Mac:**
```bash
chmod +x start-microservices.sh
./start-microservices.sh
```

### **3. Verificar estado:**
- 🌐 **API Gateway**: http://localhost
- 📚 **Core Service Docs**: http://localhost:8001/core/docs
- 📦 **Stock Service Docs**: http://localhost:8002/stock/docs
- 🏗️ **Obras Service Docs**: http://localhost:8003/obras/docs
- 📊 **Grafana**: http://localhost:3000 (admin/admin123)
- 📈 **Prometheus**: http://localhost:9090

## 🛠️ **SERVICIOS DETALLADOS**

### **🔧 Core Service (Puerto 8001)**
**Responsabilidades:**
- Panel de administración general
- Autenticación y autorización (JWT)
- Sistema de correos electrónicos
- Chat y comunicación en tiempo real
- Sistema de mensajes/notificaciones

**Endpoints principales:**
- `/core/admin/*` - Panel administrativo
- `/core/auth/*` - Autenticación
- `/core/mail/*` - Sistema de correos
- `/core/chat/*` - Chat en tiempo real
- `/core/mensajes/*` - Mensajes y notificaciones

### **📦 Stock Service (Puerto 8002)**
**Responsabilidades:**
- Gestión de inventario
- Cálculo de stock en tiempo real
- CRUD de artículos
- Reportes de inventario

**Endpoints principales:**
- `/stock/api/*` - API general de stock
- `/stock/inventory/*` - Gestión de inventario
- `/stock/articles/*` - CRUD de artículos

### **🏗️ Obras Service (Puerto 8003)**
**Responsabilidades:**
- Gestión de proyectos de obras
- Seguimiento de tareas
- Asignación de recursos
- Monitoreo de progreso

**Endpoints principales:**
- `/obras/api/*` - API general de obras
- `/obras/projects/*` - Gestión de proyectos
- `/obras/tasks/*` - Seguimiento de tareas

## 🌐 **API GATEWAY (NGINX)**

El API Gateway actúa como punto de entrada único y enruta las peticiones a los servicios correspondientes:

```nginx
/admin → core-service:8001
/auth → core-service:8001
/mail → core-service:8001
/chat → core-service:8001
/mensajes → core-service:8001
/stock → stock-service:8002
/inventory → stock-service:8002
/articles → stock-service:8002
/obras → obras-service:8003
/projects → obras-service:8003
```

## 🗄️ **BASE DE DATOS**

### **Estrategia de Base de Datos:**
- **Opción 1 (Actual)**: Base de datos compartida con esquemas separados
  - `CoreDB` - Para servicios core
  - `StockDB` - Para servicio de stock
  - `ObrasDB` - Para servicio de obras

- **Opción 2 (Futura)**: Bases de datos completamente separadas
  - Cada servicio con su propia instancia de base de datos

## 📊 **MONITOREO Y OBSERVABILIDAD**

### **Prometheus (Puerto 9090)**
- Recolección de métricas de todos los servicios
- Alertas automáticas
- Métricas custom por servicio

### **Grafana (Puerto 3000)**
- Dashboards visuales para cada servicio
- Alertas en tiempo real
- Análisis de performance

### **Health Checks**
Cada servicio expone un endpoint de salud:
- Core: `/core/health`
- Stock: `/stock/health`
- Obras: `/obras/health`
- Gateway: `/health`

## 🔒 **SEGURIDAD**

### **Autenticación Centralizada:**
- El Core Service maneja toda la autenticación
- Los demás servicios validan tokens con el Core Service
- JWT tokens compartidos entre servicios

### **Comunicación Inter-Servicios:**
- HTTPS entre servicios (en producción)
- API keys para comunicación interna
- Rate limiting en el API Gateway

## 🚢 **DESPLIEGUE**

### **Desarrollo Local:**
```bash
# Iniciar todos los servicios
./start-microservices.sh

# Ver logs específicos
docker-compose -f docker-compose.microservices.yml logs -f core-service

# Detener servicios
./stop-microservices.sh
```

### **Producción:**
1. Configurar variables de entorno específicas
2. Usar HTTPS con certificados SSL
3. Configurar límites de recursos
4. Implementar backup automático de base de datos

## 🔧 **DESARROLLO**

### **Agregar nuevo servicio:**

1. **Crear directorio:**
```bash
mkdir microservices/nuevo-service
```

2. **Crear main.py, Dockerfile, requirements.txt**

3. **Agregar al docker-compose.microservices.yml:**
```yaml
nuevo-service:
  build:
    context: ./microservices/nuevo-service
  container_name: nuevo_service
  ports:
    - "800X:800X"
  # ... resto de configuración
```

4. **Agregar rutas en nginx/microservices.conf:**
```nginx
location /nuevo {
    proxy_pass http://nuevo-service;
    # ... configuración de proxy
}
```

### **Debugging:**
```bash
# Logs en tiempo real
docker-compose -f docker-compose.microservices.yml logs -f

# Acceder a contenedor específico
docker exec -it core_service bash

# Verificar conectividad entre servicios
docker exec -it stock_service curl http://core-service:8001/core/health
```

## 📈 **BENEFICIOS OBTENIDOS**

### **✅ Ventajas de Microservicios:**
- **Escalabilidad independiente**: Cada servicio puede escalarse según demanda
- **Tecnologías específicas**: Cada servicio puede usar la tecnología más adecuada
- **Despliegue independiente**: Cambios en un servicio no afectan otros
- **Tolerancia a fallos**: Un servicio caído no tumba todo el sistema
- **Equipos especializados**: Cada equipo puede trabajar en un servicio específico

### **🔧 Mejoras de Mantenimiento:**
- Código más organizado y fácil de entender
- Testing más enfocado por servicio
- Debugging más preciso
- Actualizaciones menos riesgosas

## 🛣️ **ROADMAP FUTURO**

### **Fase 1 (Completada):**
- ✅ Separación de Core, Stock y Obras
- ✅ API Gateway configurado
- ✅ Monitoreo básico

### **Fase 2 (En Progreso):**
- 🔄 Migración de servicios restantes (tickets, widgets)
- 🔄 Implementación de circuit breakers
- 🔄 Cache distribuido (Redis)

### **Fase 3 (Planificada):**
- 📋 Bases de datos completamente separadas
- 📋 Kubernetes deployment
- 📋 CI/CD pipelines por servicio
- 📋 Service mesh (Istio)

## 📞 **SOPORTE**

### **Comandos útiles:**
```bash
# Estado de servicios
docker-compose -f docker-compose.microservices.yml ps

# Reiniciar servicio específico
docker-compose -f docker-compose.microservices.yml restart stock-service

# Limpiar completamente
docker-compose -f docker-compose.microservices.yml down -v
docker system prune -f
```

### **Contacto:**
- 📧 Email: tu@email.com
- 📱 Slack: #microservices-support
- 📋 Issues: [GitHub Issues](link-to-github)

---
**Última actualización**: $(date)
**Versión**: 1.0.0
