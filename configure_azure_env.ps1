# Script para configurar variables de entorno en Azure App Service
# Ejecutar con: .\configure_azure_env.ps1

$appName = "demoEcomerce"
$resourceGroup = "Ecomerce_test"
$subscription = "e08987ee-0468-4b1f-bcab-cf039163ccb6"

Write-Host "Configurando variables de entorno en Azure App Service..." -ForegroundColor Cyan

# Configurar variables de entorno básicas
$envVars = @{
    "SECRET" = "<REPLACE_WITH_YOUR_SECRET>"
    "ALGORITHM" = "HS256"
    "ACCESS_TOKEN_DURATION" = "30"
    "FRONTEND_URL" = "https://demoecomerce.azurewebsites.net"
    "BACKEND_URL" = "https://demoecomerce.azurewebsites.net"
    "ORIGINS" = "https://demoecomerce.azurewebsites.net,https://demoecomerce-fmb7asd5h0f5epdn.chilecentral-01.azurewebsites.net"
    "ENVIRONMENT" = "production"
    "STATIC_DIR" = "static"

    # Base de datos - SQL Server Azure
    "DB_TYPE" = "sqlserver"
    "DB_USER" = "Juadmin"
    "DB_PASSWORD" = "<REPLACE_WITH_DB_PASSWORD>"
    "DB_HOST" = "dbdemoecomerce.database.windows.net"
    "DB_NAME" = "db_ecomerce"
    "USE_PYMSSQL" = "true"
    "DB_DRIVER" = "ODBC Driver 17 for SQL Server"
    "POOL_SIZE" = "5"
    "MAX_OVERFLOW" = "10"
    "POOL_TIMEOUT" = "30"
    "POOL_PRE_PING" = "true"
    "POOL_RECYCLE" = "3600"

    # Desactivar características que requieren servicios externos
    "MERCADOPAGO_ACCESS_TOKEN" = "<REPLACE_WITH_MERCADOPAGO_ACCESS_TOKEN>"
    "MERCADOPAGO_PUBLIC_KEY" = "<REPLACE_WITH_MERCADOPAGO_PUBLIC_KEY>"
    "GOOGLE_CLIENT_ID" = ""
    "GOOGLE_CLIENT_SECRET" = ""
}

Write-Host "`nEjecuta estos comandos en Azure CLI (instálalo primero si no lo tienes):" -ForegroundColor Yellow
Write-Host "winget install Microsoft.AzureCLI" -ForegroundColor Gray
Write-Host "`nDespués ejecuta:" -ForegroundColor Yellow

foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    Write-Host "az webapp config appsettings set --name $appName --resource-group $resourceGroup --subscription $subscription --settings `"$key=$value`"" -ForegroundColor Green
}

Write-Host "`nO usa este comando único para todas las variables:" -ForegroundColor Yellow
$allSettings = ($envVars.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join " "
Write-Host "az webapp config appsettings set --name $appName --resource-group $resourceGroup --subscription $subscription --settings $allSettings" -ForegroundColor Green
