@description('Globally unique Azure Web App name.')
param appName string

@description('Azure region for the App Service plan and web app.')
param location string = resourceGroup().location

@description('App Service plan SKU. B1 supports Always On; F1 is free but cold-starts.')
@allowed([
  'F1'
  'B1'
  'S1'
])
param sku string = 'B1'

@description('Linux Python runtime, pinned inside the AEGIS interpreter range.')
param linuxFxVersion string = 'PYTHON|3.12'

var isFree = sku == 'F1'
var skuTier = sku == 'F1' ? 'Free' : (sku == 'B1' ? 'Basic' : 'Standard')

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${appName}-plan'
  location: location
  kind: 'linux'
  sku: {
    name: sku
    tier: skuTier
  }
  properties: {
    reserved: true
  }
}

resource web 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: plan.id
    reserved: true
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      appCommandLine: 'bash deploy/containers/startup.sh'
      alwaysOn: !isFree
      ftpsState: 'Disabled'
      http20Enabled: true
      minTlsVersion: '1.2'
      healthCheckPath: '/healthz'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
        {
          name: 'AEGIS_RUNTIME_MODE'
          value: 'ui'
        }
        {
          name: 'AEGIS_LLM_ENABLED'
          value: 'false'
        }
      ]
    }
  }
}

output defaultHostName string = web.properties.defaultHostName
output webAppName string = web.name
