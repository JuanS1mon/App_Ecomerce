# Script para verificar el estado del deployment en Azure
# Requiere Azure CLI instalado

Write-Host "=== Verificacion de Deployment de Azure ===" -ForegroundColor Cyan
Write-Host ""

# Información del último commit
Write-Host "📦 Último commit:" -ForegroundColor Yellow
git log --oneline -1
Write-Host ""

# Verificar si Azure CLI está instalado
$azInstalled = Get-Command az -ErrorAction SilentlyContinue

if ($azInstalled) {
    Write-Host "✅ Azure CLI detectado" -ForegroundColor Green
    Write-Host ""
    
    # Información del App Service
    Write-Host "🌐 Estado del App Service:" -ForegroundColor Yellow
    az webapp show --name EcomerceApp --resource-group ecomerce_test --query '{name:name, state:state, defaultHostName:defaultHostName}' -o table 2>$null
    
    Write-Host ""
    Write-Host "📋 Últimos deployments:" -ForegroundColor Yellow
    az webapp deployment list --name EcomerceApp --resource-group ecomerce_test --query '[0:3].{status:status, active:active, start:start_time, author:author}' -o table 2>$null
    
    Write-Host ""
    Write-Host "📊 Para ver logs en tiempo real, ejecuta:" -ForegroundColor Cyan
    Write-Host "   az webapp log tail --name EcomerceApp --resource-group ecomerce_test" -ForegroundColor White
} else {
    Write-Host "⚠️  Azure CLI no está instalado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para monitorear el deployment:" -ForegroundColor Cyan
    Write-Host "1. Ve al Portal de Azure: https://portal.azure.com" -ForegroundColor White
    Write-Host "2. Busca tu App Service: EcomerceApp" -ForegroundColor White
    Write-Host "3. Ve a 'Deployment Center' para ver el progreso" -ForegroundColor White
    Write-Host "4. Ve a 'Log stream' para ver logs en tiempo real" -ForegroundColor White
}

Write-Host ""
Write-Host "🔗 Links útiles:" -ForegroundColor Cyan
Write-Host "   GitHub Actions: https://github.com/JuanS1mon/App_Ecomerce/actions" -ForegroundColor White
Write-Host "   Azure Portal: https://portal.azure.com" -ForegroundColor White
Write-Host "   App URL: https://ecomerceapp.azurewebsites.net" -ForegroundColor White
Write-Host ""

# Intentar hacer ping a la aplicación
Write-Host "🔍 Verificando si la app responde..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://ecomerceapp.azurewebsites.net" -Method Head -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ La aplicación está ONLINE (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ La aplicación no responde o está reiniciando" -ForegroundColor Red
    Write-Host "   Esto es normal durante un deployment" -ForegroundColor Yellow
}
