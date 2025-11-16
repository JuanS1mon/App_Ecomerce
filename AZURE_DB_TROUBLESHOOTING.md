# Verificación de Conectividad Azure SQL Database

## Tu Configuración Actual

```
DB_HOST: dbdemoecomerce.database.windows.net
DB_NAME: db_ecomerce
DB_USER: Juadmin
DB_DRIVER: ODBC Driver 18 for SQL Server
```

## Pasos para Verificar y Arreglar

### 1. Verificar Firewall de Azure SQL Database

Tu App Service necesita acceso a la base de datos:

1. Ve al Azure Portal
2. Busca tu SQL Server: **dbdemoecomerce**
3. En el menú izquierdo, ve a **Security** → **Networking**
4. En la sección **Firewall rules**, asegúrate de tener:
   - ✅ **"Allow Azure services and resources to access this server"** = **ON**
5. Guarda los cambios

### 2. Verificar Driver ODBC

El driver "ODBC Driver 18 for SQL Server" requiere configuración especial de SSL.

**Opciones:**

#### Opción A: Usar Driver 17 (Más Simple)
Cambia en Azure Portal:
```
DB_DRIVER = ODBC Driver 17 for SQL Server
```

#### Opción B: Mantener Driver 18 pero agregar parámetros
Necesitas modificar el código de conexión para incluir:
```
Encrypt=yes;TrustServerCertificate=no
```

### 3. Cambio CRÍTICO: SCM_DO_BUILD_DURING_DEPLOYMENT

**PROBLEMA:** Tienes `SCM_DO_BUILD_DURING_DEPLOYMENT = 1`

Esto hace que Azure ignore tu `.deployment` file y active Oryx, lo que causa el conflicto de `typing_extensions`.

**SOLUCIÓN:** En Azure Portal → Configuration → Application Settings:
- Cambia `SCM_DO_BUILD_DURING_DEPLOYMENT` a `false`
- O bórrala completamente

### 4. Agregar Variable Faltante (Opcional para mejor logging)

Considera agregar:
```
WEBSITES_ENABLE_APP_SERVICE_STORAGE = true
```

## Cambios Recomendados en Azure Portal

| Variable | Valor Actual | Valor Recomendado | Razón |
|----------|--------------|-------------------|--------|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `1` | `false` o borrar | Conflicto con venv pre-construido |
| `DB_DRIVER` | `ODBC Driver 18...` | `ODBC Driver 17...` | Evitar problemas SSL |

## Comando para Probar Conexión a DB (después de los cambios)

Una vez hagas los cambios, la app debería poder:
1. Conectarse a Azure SQL Database
2. Crear las tablas necesarias
3. Responder correctamente en https://demoecomerce.azurewebsites.net

## Si Persiste el Error

Revisa los logs de la aplicación en Azure Portal:
1. Ve a tu App Service
2. **Monitoring** → **Log stream**
3. Busca errores relacionados con conexión a base de datos
