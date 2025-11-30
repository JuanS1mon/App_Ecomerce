# Despliegue - App_Ecomerce (FastAPI + SQL Server)

Este README incluye instrucciones para desplegar la API FastAPI en Azure App Service (sin contenedor). Sigue los pasos para crear el plan, Web App, importar variables de entorno y automatizar con GitHub Actions.

## 1) Requisitos previos
- Tener `az` CLI instalado y `az login` autorizado.
- Tener permisos para crear recursos en el subscription y el Resource Group `Recur_test`.
- Tener el publish profile de la App Service si quieres usar GitHub Actions con `AZURE_WEBAPP_PUBLISH_PROFILE`.
- (Opcional) Azure SQL Server ya creado con DB, o datos de conexión.

## 2) Crear App Service (script)
Se incluye `scripts/azure_setup.ps1` que crea plan y App Service y configura las opciones básicas (Always On, startup command y log config).

Ejecutar:
```powershell
# Ajustar variables si hace falta
.
.
# ejemplo
.
.
# Despliegue manual
.
```

## 3) Importar variables de `.env`
Se incluye `scripts/import_env_to_appsettings.ps1` que lee el archivo `.env` y sube las variables a App Settings; las variables sensibles se marcan como `slotSetting`.

Ejecutar:
```powershell
.
\scripts\import_env_to_appsettings.ps1 -rg "Recur_test" -app "App_Ecomerce" -envFile ".env"
```

## 4) GitHub Actions - CI/CD
- `.github/workflows/zip-deploy.yml` hace `pip install -r requirements.txt`, crea zip y despliega a App Service (master branch).
- Agrega `AZURE_WEBAPP_PUBLISH_PROFILE` en GitHub repository secrets.

## 5) Debug y logs
- Streaming logs:
```powershell
az webapp log tail -g Recur_test -n App_Ecomerce
```
- App settings:
```powershell
az webapp config appsettings list -g Recur_test -n App_Ecomerce
```

## 6) Notas y recomendaciones de seguridad
- No subas secretos en texto plano al repo. Usa Key Vault y Managed Identity para producción.
- Evita `ORIGINS=*` en producción: configura tu frontend real.
- Reemplaza `sa` por un usuario con permisos mínimos.
- Si usas pyodbc y ODBC driver, considera un contenedor. App Service Linux no trae drivers ODBC por defecto.
