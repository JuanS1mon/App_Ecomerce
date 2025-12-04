# 🚀 Guía de Configuración - Variables de Entorno en Azure

## 📋 Configuración de Secrets en GitHub

Después de cambiar a usar variables de entorno directamente desde el `.env`, necesitas configurar las siguientes **secrets** en tu repositorio de GitHub:

### 1. Ve a tu repositorio en GitHub
- Ve a **Settings** → **Secrets and variables** → **Actions**

### 2. Crea las siguientes Repository Secrets:

#### 🔐 Secrets de Azure (Reemplaza con tus valores reales)
```
AZURE_CLIENT_ID=tu-client-id-de-azure
AZURE_TENANT_ID=tu-tenant-id-de-azure
AZURE_SUBSCRIPTION_ID=tu-subscription-id-de-azure
```

#### 📝 Cómo obtener las credenciales de Azure:

1. **Ve al Portal de Azure**: https://portal.azure.com
2. **Busca "Microsoft Entra ID"** (antes Active Directory)
3. **Ve a "App registrations"**
4. **Crea una nueva aplicación** o usa una existente
5. **En "Certificates & secrets"** → **Client secrets** → **New client secret**
6. **Copia el Client ID, Tenant ID y Subscription ID**

### 3. Permisos necesarios en Azure

La aplicación debe tener permisos de **Contributor** en el App Service. Para configurar:

1. **Ve al App Service** en Azure Portal
2. **Ve a "Access control (IAM)"**
3. **Add role assignment**
4. **Selecciona "Contributor"** para tu aplicación registrada

## ✅ Ventajas de este enfoque

- ✅ **Más seguro**: Las variables sensibles no están en el código
- ✅ **Más flexible**: Puedes cambiar variables sin redeploy
- ✅ **Mejor control**: Gestión centralizada en Azure Portal
- ✅ **Sin .env en Git**: No hay riesgo de subir credenciales

## 🔄 Variables configuradas automáticamente

El workflow configura estas variables en Azure App Service:

- `DB_TYPE`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`
- `SMTP_SERVER`, `SMTP_PORT`, `USERNAME_EMAIL`, `PASSWORD_EMAIL`
- `SECRET`, `ALGORITHM`, `ACCESS_TOKEN_DURATION`
- `ENVIRONMENT=production`, `BASE_URL`, `FRONTEND_URL`
- `MERCADOPAGO_ACCESS_TOKEN`, `MERCADOPAGO_PUBLIC_KEY`
- `ORIGINS`

## 🚀 Próximos pasos

1. **Configura las secrets** en GitHub
2. **Push a la rama** `chore/ci-zip-deploy`
3. **Monitorea el deployment** en GitHub Actions
4. **Verifica la app** en `https://ecomerceapp.azurewebsites.net`

¿Necesitas ayuda con algún paso específico?</content>
<parameter name="filePath">c:\Users\PCJuan\Desktop\sql_app_Ecomerce\AZURE_SECRETS_SETUP.md