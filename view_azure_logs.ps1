# Script para ver los logs de Azure App Service
# Como no tienes Azure CLI instalado, usa el Azure Portal

Write-Host "Para ver los logs de tu aplicación:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opción 1: Azure Portal - Log Stream" -ForegroundColor Yellow
Write-Host "1. Ve a: https://portal.azure.com" -ForegroundColor White
Write-Host "2. Busca tu App Service: demoEcomerce" -ForegroundColor White
Write-Host "3. En el menú izquierdo: Monitoring -> Log stream" -ForegroundColor White
Write-Host "4. Selecciona: Application logs" -ForegroundColor White
Write-Host "5. Verás los logs en tiempo real" -ForegroundColor White
Write-Host ""
Write-Host "Opción 2: Diagnose and Solve Problems" -ForegroundColor Yellow
Write-Host "1. En tu App Service: demoEcomerce" -ForegroundColor White
Write-Host "2. Menú izquierdo: Diagnose and solve problems" -ForegroundColor White
Write-Host "3. Busca: 'Application Logs'" -ForegroundColor White
Write-Host ""
Write-Host "Opción 3: Advanced Tools (Kudu)" -ForegroundColor Yellow
Write-Host "1. En tu App Service: demoEcomerce" -ForegroundColor White
Write-Host "2. Menú izquierdo: Development Tools -> Advanced Tools" -ForegroundColor White
Write-Host "3. Click 'Go'" -ForegroundColor White
Write-Host "4. En el menú superior: Debug console -> CMD" -ForegroundColor White
Write-Host "5. Navega a: LogFiles/Application" -ForegroundColor White
Write-Host ""
Write-Host "O accede directamente a Kudu:" -ForegroundColor Yellow
Write-Host "https://demoecomerce.scm.azurewebsites.net/DebugConsole" -ForegroundColor Green
Write-Host ""
Write-Host "Busca estos posibles errores:" -ForegroundColor Cyan
Write-Host "  - Connection timeout (problema de red con SQL Database)" -ForegroundColor White
Write-Host "  - Login failed (usuario/contraseña incorrectos)" -ForegroundColor White
Write-Host "  - Cannot open database (firewall bloqueando)" -ForegroundColor White
Write-Host "  - ImportError o ModuleNotFoundError (falta algún paquete)" -ForegroundColor White
Write-Host ""
