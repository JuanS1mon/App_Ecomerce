<#
  azure_setup.ps1
  Script helper para crear App Service plan, crear web app y configurar startup command y opciones basicas
  No incluye credenciales sensibles. Ejecutá localmente desde PowerShell con az login.
#>

param(
    [string]$rg = "Recur_test",
    [string]$app = "App_Ecomerce",
    [string]$plan = "appservice-plan-ecomerce",
    [string]$location = "brazilsouth",
    [string]$sku = "B1",
    [string]$runtime = "PYTHON:3.11"
)

Write-Host "Ensure you're logged into Azure and set the right subscription"
Write-Host "Creating or ensuring App Service Plan exists: $plan in $rg ($location)"

az group create --name $rg --location $location | Out-Null

# Create App Service Plan
az appservice plan create --name $plan --resource-group $rg --is-linux --sku $sku --location $location | Out-Null

# Create Web App
az webapp create --resource-group $rg --plan $plan --name $app --runtime $runtime --deployment-local-git | Out-Null

# Set startup command to use Gunicorn + Uvicorn worker using the $PORT variable set by Azure
$startup = "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:$PORT --timeout 600"
az webapp config set --resource-group $rg --name $app --startup-file $startup | Out-Null

# Enable Always On and HTTPS-only
az webapp config set --resource-group $rg --name $app --always-on true --https-only true | Out-Null

# Configure Logging
az webapp log config --name $app --resource-group $rg --application-logging true --detailed-error-messages true --failed-request-tracing true | Out-Null

Write-Host "Web App $app created/updated in $rg with startup command: $startup"
Write-Host "Check logs with: az webapp log tail -g $rg -n $app"
