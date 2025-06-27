@description('Name of the environment')
param suffixName string

@description('Azure region for resources')
param location string = resourceGroup().location

@secure()
param apiKey string

@secure()
param apiEndpoint string

@description('Docker image for the app service')
param dockerImage string

@description('Tags to apply to all resources')
param tags object

// App Service Plan using Azure Verified Module
module appServicePlan 'br/public:avm/res/web/serverfarm:0.3.0' = {
  name: 'appServicePlan'
  params: {
    name: 'asp-azureupdatepptx-${suffixName}'
    location: location
    skuName: 'B1'
    kind: 'Linux'
    tags: tags
  }
}

// App Service using Azure Verified Module
module appService 'br/public:avm/res/web/site:0.11.0' = {
  name: 'appService'
  params: {
    name: 'app-azureupdatepptx-${suffixName}'
    location: location
    kind: 'app,linux,container'
    serverFarmResourceId: appServicePlan.outputs.resourceId
    siteConfig: {
      alwaysOn: false
      linuxFxVersion: 'DOCKER|${dockerImage}'
      appSettings: [
        {
          name: 'API_KEY'
          value: apiKey
        }
        {
          name: 'API_ENDPOINT'
          value: apiEndpoint
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
      ]
    }
    httpsOnly: true
    tags: tags
  }
}

// Outputs
output appServiceUrl string = 'https://${appService.outputs.defaultHostname}'
output appServiceName string = appService.outputs.name
