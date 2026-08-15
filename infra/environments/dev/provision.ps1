# Provision the Linux Python App Service. Names only — no secrets.
param(
    [Parameter(Mandatory = $true)]
    [string]$AppName,
    [string]$ResourceGroup = "rg-aegis-dev",
    [string]$Location = "eastus",
    [ValidateSet("F1", "B1", "S1")]
    [string]$Sku = "B1"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

az group create --name $ResourceGroup --location $Location
az deployment group create `
    --resource-group $ResourceGroup `
    --template-file (Join-Path $here "main.bicep") `
    --parameters appName=$AppName sku=$Sku location=$Location

Write-Host "Download the publish profile and store it as GitHub secret AZURE_WEBAPP_PUBLISH_PROFILE:"
Write-Host "  az webapp deployment list-publishing-profiles --resource-group $ResourceGroup --name $AppName --xml"
