# Guía para Configurar Azure App Service - demoEcomerce

## Problema Actual
La aplicación muestra "Application Error" porque faltan variables de entorno necesarias.

## Solución: Configurar Variables de Entorno en Azure Portal

### Opción 1: Portal de Azure (MÁS FÁCIL)

1. Ve a Azure Portal: https://portal.azure.com
2. Navega a tu App Service: **demoEcomerce**
3. En el menú izquierdo, busca: **Configuration** (Configuración)
4. Haz clic en **Application settings** (Configuración de la aplicación)
5. Agrega estas variables una por una haciendo clic en **+ New application setting**:

```
SECRET = azure-production-secret-key-741445767
ALGORITHM = HS256
ACCESS_TOKEN_DURATION = 30
FRONTEND_URL = https://demoecomerce.azurewebsites.net
BACKEND_URL = https://demoecomerce.azurewebsites.net
ORIGINS = https://demoecomerce.azurewebsites.net,https://demoecomerce-fmb7asd5h0f5epdn.chilecentral-01.azurewebsites.net
ENVIRONMENT = production
STATIC_DIR = static
DB_TYPE = sqlite
DB_NAME = sqlapp.db
```

6. Después de agregar todas, haz clic en **Save** (Guardar)
7. La aplicación se reiniciará automáticamente

### Opción 2: Azure CLI (Requiere instalación)

#### Instalar Azure CLI primero:
```powershell
winget install Microsoft.AzureCLI
```

#### Luego ejecuta este comando:
```bash
az webapp config appsettings set --name demoEcomerce --resource-group Ecomerce_test --subscription e08987ee-0468-4b1f-bcab-cf039163ccb6 --settings SECRET="azure-production-secret-key-741445767" ALGORITHM="HS256" ACCESS_TOKEN_DURATION="30" FRONTEND_URL="https://demoecomerce.azurewebsites.net" BACKEND_URL="https://demoecomerce.azurewebsites.net" ORIGINS="https://demoecomerce.azurewebsites.net,https://demoecomerce-fmb7asd5h0f5epdn.chilecentral-01.azurewebsites.net" ENVIRONMENT="production" STATIC_DIR="static" DB_TYPE="sqlite" DB_NAME="sqlapp.db"
```

## Variables Explicadas

- **SECRET**: Clave secreta para JWT (tokens de autenticación)
- **DB_TYPE**: Tipo de base de datos - usando SQLite para simplicidad
- **DB_NAME**: Nombre del archivo de base de datos SQLite
- **FRONTEND_URL/BACKEND_URL**: URLs de tu aplicación en Azure
- **ORIGINS**: URLs permitidas para CORS (seguridad)
- **ENVIRONMENT**: production (para modo producción)

## Después de Configurar

1. Espera 1-2 minutos para que la app se reinicie
2. Visita: https://demoecomerce.azurewebsites.net
3. Deberías ver tu aplicación funcionando

## Nota sobre Base de Datos

Actualmente configuré SQLite para simplicidad. Si necesitas SQL Server:
1. Crea una Azure SQL Database
2. Cambia DB_TYPE a "sqlserver"
3. Agrega: DB_HOST, DB_USER, DB_PASSWORD, DB_DRIVER
