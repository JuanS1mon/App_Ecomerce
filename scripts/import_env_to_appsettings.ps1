<#
    import_env_to_appsettings.ps1
    Lee '.env' y sube los valores como App Settings a la Web App de Azure
    - Evitar exponer secretos en logs
    - Marcar variables sensibles como slotSetting=true para que no sean swappeadas con slots
#>

param(
    [string]$rg = "Recur_test",
    [string]$app = "App_Ecomerce",
    [string]$envFile = ".env"
)

if (-Not (Test-Path $envFile)) {
    Write-Error "No se encontró $envFile en la ruta actual. Sitúate en la carpeta raíz del repo antes de ejecutar este script."
    exit 1
}

# Lista de variables que consideraremos sensibles
$secrets = @(
    "DB_PASSWORD",
    "SECRET",
    "PASSWORD_EMAIL",
    "MERCADOPAGO_ACCESS_TOKEN"
)

Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and -not $line.StartsWith("//")) {
        $idx = $line.IndexOf("=")
        if ($idx -gt -1) {
            $name = $line.Substring(0, $idx).Trim()
            $value = $line.Substring($idx + 1).Trim()
            # Remove surrounding quotes
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }

            if (-not [string]::IsNullOrEmpty($name)) {
                if ($secrets -contains $name) {
                    Write-Host "Setting secret (slotSetting=true): $name"
                    az webapp config appsettings set --resource-group $rg --name $app --settings "$name=$value" --slot-setting true > $null
                } else {
                    Write-Host "Setting: $name"
                    az webapp config appsettings set --resource-group $rg --name $app --settings "$name=$value" > $null
                }
            }
        }
    }
}

Write-Host "Import finished. Revisa App Settings en el Portal o con: az webapp config appsettings list -g $rg -n $app"
