# 🚀 Guía de Deployment a Azure App Service desde GitHub

Esta guía te ayudará a desplegar tu aplicación FastAPI de ecommerce en Azure usando la importación directa desde GitHub.

## 📋 Prerrequisitos

- ✅ Cuenta de Azure activa
- ✅ Repositorio de GitHub con el código
- ✅ Base de datos SQL Server (puedes usar Azure SQL Database)
- ✅ Credenciales configuradas en tu archivo `.env` local

## 🔧 Archivos de Configuración Creados

### 1. `startup.txt`
Comando que Azure usará para iniciar tu aplicación:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0 --timeout 600
```

### 2. `runtime.txt`
Especifica la versión de Python:
```
python-3.11
```

### 3. `.deployment`
Indica a Azure que debe ejecutar build durante el deployment:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

## 📦 Paso 1: Preparar el Repositorio GitHub

### 1.1. Verificar .gitignore
Ya está actualizado para excluir:
- ❌ Archivos `.env` (credenciales)
- ❌ Entornos virtuales (`env/`, `venv/`)
- ❌ Archivos de Azure específicos
- ❌ Logs y caché

### 1.2. Commit y Push de los cambios
```bash
git add .
git commit -m "Preparado para deployment en Azure"
git push origin main
```

⚠️ **IMPORTANTE**: Nunca subas el archivo `.env` con tus credenciales

## ☁️ Paso 2: Crear Azure App Service

### 2.1. Ir al Portal de Azure
1. Accede a [portal.azure.com](https://portal.azure.com)
2. Busca "App Services" en la barra de búsqueda
3. Click en **"+ Create"** o **"+ Crear"**

### 2.2. Configuración Básica

#### **Subscription y Resource Group**
- Selecciona tu suscripción
- Crea o selecciona un Resource Group (ej: `rg-ecommerce-app`)

#### **Instance Details**
- **Name**: `tu-app-ecommerce` (será: `tu-app-ecommerce.azurewebsites.net`)
- **Publish**: Code
- **Runtime stack**: Python 3.11
- **Operating System**: Linux
- **Region**: Elige la más cercana (ej: East US, Brazil South)

#### **Pricing Plan**
- Para empezar: **Basic B1** (económico, ~$13/mes)
- Para producción: **Standard S1** o superior

### 2.3. Click en **"Review + Create"** y luego **"Create"**

## 🔗 Paso 3: Conectar con GitHub

### 3.1. En tu App Service
1. Ve a **"Deployment Center"** en el menú lateral
2. En **Source**, selecciona **"GitHub"**
3. Click en **"Authorize"** para conectar tu cuenta de GitHub

### 3.2. Configurar el Repositorio
- **Organization**: Tu usuario de GitHub
- **Repository**: Selecciona tu repositorio
- **Branch**: `main` (o la rama que uses)

### 3.3. Click en **"Save"**
Azure automáticamente:
- Clonará el repositorio
- Instalará las dependencias de `requirements.txt`
- Ejecutará el comando de `startup.txt`

## ⚙️ Paso 4: Configurar Variables de Entorno

### 4.1. Ir a Configuration
1. En tu App Service, ve a **"Configuration"** (menú lateral)
2. Click en **"+ New application setting"**

### 4.2. Agregar Variables de Entorno
Configura **TODAS** las variables de tu archivo `.env`:

#### Variables Esenciales:
```plaintext
SECRET = tu-clave-secreta-super-segura
ALGORITHM = HS256
ACCESS_TOKEN_DURATION = 30

DB_TYPE = sqlserver
DB_USER = tu-usuario-sql
DB_PASSWORD = tu-password-sql
DB_HOST = tu-servidor.database.windows.net
DB_NAME = nombre-base-datos
DB_DRIVER = ODBC Driver 18 for SQL Server

FRONTEND_URL = https://tu-app-ecommerce.azurewebsites.net
BACKEND_URL = https://tu-app-ecommerce.azurewebsites.net
ORIGINS = https://tu-app-ecommerce.azurewebsites.net

ENVIRONMENT = production
```

#### Variables Opcionales (MercadoPago, Google OAuth, etc.):
```plaintext
MERCADOPAGO_ACCESS_TOKEN = tu-token-mercadopago
MERCADOPAGO_PUBLIC_KEY = tu-public-key-mercadopago

GOOGLE_CLIENT_ID = tu-client-id-google
GOOGLE_CLIENT_SECRET = tu-secret-google
GOOGLE_REDIRECT_URI = https://tu-app-ecommerce.azurewebsites.net/auth/google/callback
```

### 4.3. Agregar Connection String para la Base de Datos
Si usas Azure SQL Database:
1. Ve a la pestaña **"Connection strings"**
2. Agrega tu connection string de SQL Server

### 4.4. Click en **"Save"** (arriba)
⚠️ Esto reiniciará la aplicación

## 🗄️ Paso 5: Configurar Azure SQL Database (Opcional)

Si no tienes una base de datos:

### 5.1. Crear Azure SQL Database
1. Busca "SQL Database" en Azure
2. Click en **"+ Create"**
3. Configura:
   - **Database name**: `ecommerce_db`
   - **Server**: Crea uno nuevo
   - **Pricing tier**: Basic (para empezar)

### 5.2. Configurar Firewall
1. En tu SQL Server, ve a **"Firewalls and virtual networks"**
2. Activa **"Allow Azure services and resources to access this server"**
3. Agrega tu IP si necesitas conectarte desde tu PC

### 5.3. Obtener Connection String
1. En tu Database, ve a **"Connection strings"**
2. Copia la cadena de conexión
3. Agrégala a las variables de entorno del App Service

## ✅ Paso 6: Verificar el Deployment

### 6.1. Monitorear el Build
1. En **"Deployment Center"**, ve a la pestaña **"Logs"**
2. Verifica que el deployment fue exitoso (✅)

### 6.2. Ver Logs de Aplicación
```bash
# Desde tu terminal local (instala Azure CLI primero)
az webapp log tail --name tu-app-ecommerce --resource-group rg-ecommerce-app
```

O desde el portal:
1. Ve a **"Log stream"** en el menú lateral
2. Observa los logs en tiempo real

### 6.3. Probar la Aplicación
Abre tu navegador y ve a:
```
https://tu-app-ecommerce.azurewebsites.net
```

Prueba también:
- `/docs` - Documentación de la API
- `/admin` - Panel administrativo

## 🔄 Paso 7: Actualizaciones Continuas

Cada vez que hagas push a tu rama en GitHub:
```bash
git add .
git commit -m "Nueva funcionalidad"
git push origin main
```

Azure automáticamente:
1. Detectará el cambio
2. Ejecutará un nuevo build
3. Desplegará la nueva versión

## 🐛 Troubleshooting

### Error 500 - Internal Server Error
1. Ve a **"Log stream"** para ver los errores
2. Verifica las variables de entorno
3. Asegúrate de que la base de datos es accesible

### No se instalan las dependencias
1. Verifica que `requirements.txt` esté en la raíz
2. Verifica que `.deployment` esté configurado

### La aplicación no inicia
1. Verifica `startup.txt`
2. Asegúrate de que `main.py` existe y la variable `app` está definida
3. Revisa los logs: puede ser falta de conexión a BD

### Base de datos no se conecta
1. Verifica las credenciales en Configuration
2. Asegúrate de que el firewall de Azure SQL permite conexiones desde Azure
3. Usa `ODBC Driver 18 for SQL Server` para Azure SQL

## 📊 Comandos Útiles de Azure CLI

```bash
# Ver logs en tiempo real
az webapp log tail --name tu-app-ecommerce --resource-group rg-ecommerce-app

# Reiniciar la aplicación
az webapp restart --name tu-app-ecommerce --resource-group rg-ecommerce-app

# Ver configuración
az webapp config appsettings list --name tu-app-ecommerce --resource-group rg-ecommerce-app

# SSH a tu contenedor (troubleshooting avanzado)
az webapp ssh --name tu-app-ecommerce --resource-group rg-ecommerce-app
```

## 🔐 Mejores Prácticas de Seguridad

1. ✅ **Nunca** subas archivos `.env` a GitHub
2. ✅ Usa **Azure Key Vault** para secretos en producción
3. ✅ Configura **HTTPS only** en tu App Service
4. ✅ Usa **Managed Identity** para conectar con Azure SQL
5. ✅ Mantén actualizadas las dependencias
6. ✅ Configura **Application Insights** para monitoreo

## 📚 Recursos Adicionales

- [Azure App Service Docs](https://docs.microsoft.com/azure/app-service/)
- [FastAPI on Azure](https://docs.microsoft.com/azure/developer/python/tutorial-deploy-app-service-on-linux)
- [Azure SQL Database](https://docs.microsoft.com/azure/azure-sql/)

## 🎉 ¡Listo!

Tu aplicación FastAPI de ecommerce ahora está desplegada en Azure. Cada push a GitHub actualizará automáticamente la aplicación.

---

**Creado**: Noviembre 2025
**Versión**: 1.0
