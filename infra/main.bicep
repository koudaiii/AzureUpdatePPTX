targetScope = 'subscription'

@description('suffix for environment name, e.g. dev, prod')
param suffixName string

@description('Azure region for resources')
param location string = 'Australia East'

@description('Docker image for the app service')
param dockerImage string = 'koudaiii/azureupdatepptx:latest'

@secure()
@description('api key for the app service')
param apiKey string

@secure()
@description('api endpoint for the app service')
param apiEndpoint string

@description('Tags to apply to all resources')
param tags object = {
  project: 'AzureUpdatePPTX'
  managed_by: 'bicep'
}

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'rg-azureupdatepptx-${suffixName}'
  location: location
  tags: tags
}

// Deploy resources in the resource group
module resources 'modules/resources.bicep' = {
  scope: rg
  name: 'resources'
  params: {
    suffixName: suffixName
    location: location
    dockerImage: dockerImage
    tags: tags
    apiKey: apiKey
    apiEndpoint: apiEndpoint
  }
}

// Outputs
output appServiceUrl string = resources.outputs.appServiceUrl
output resourceGroupName string = rg.name
